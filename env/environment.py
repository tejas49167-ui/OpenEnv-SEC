from __future__ import annotations

import uuid
from typing import Dict, Optional

from env.data import load_examples
from env.models import (
    TASK_LABELS,
    Action,
    EnvironmentState,
    Observation,
    Reward,
    StepInfo,
    TaskName,
    build_environment_metadata,
)
from env.reward import GRADERS, compute_reward
from env.scoring import clamp_open_unit_interval
from env.tasks import TASKS

try:
    from openenv.core.env_server.interfaces import Environment as OpenEnvEnvironment
except ImportError:  # pragma: no cover
    class OpenEnvEnvironment:
        SUPPORTS_CONCURRENT_SESSIONS = False

        def __init__(self, *args, **kwargs) -> None:
            pass


ACTION_TO_ARTIFACT = {
    "inspect_payload": "payload_analysis",
    "decode_obfuscation": "decoded_input",
    "review_history": "traffic_history",
    "check_source_reputation": "source_reputation",
    "inspect_asset_context": "asset_context",
    "consult_playbook": "playbook_guidance",
}

ALL_ACTIONS = list(ACTION_TO_ARTIFACT.keys()) + ["submit_triage"]

SEVERITY_TO_PRIORITY = {
    "none": "P4",
    "low": "P3",
    "medium": "P2",
    "high": "P1",
    "critical": "P0",
}


class CyberVulnerabilityTriageEnvironment(OpenEnvEnvironment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self, task: TaskName = "easy") -> None:
        super().__init__()
        self.examples = load_examples()
        self._cursor_by_task: Dict[TaskName, int] = {"easy": 0, "medium": 0, "hard": 0}
        self._state = EnvironmentState(
            current_task=task,
            max_steps=TASKS[task].max_steps,
            episode_id=str(uuid.uuid4()),
            step_count=0,
        )
        self._current_example = None

    def _derive_service(self) -> str:
        if self._current_example is None:
            return "unknown-service"
        if self._current_example.service:
            return self._current_example.service
        path = self._current_example.path
        if path.startswith("/login") or path.startswith("/account"):
            return "identity-web"
        if path.startswith("/orders") or path.startswith("/products") or path.startswith("/search"):
            return "commerce-frontend"
        if path.startswith("/api/archive") or path.startswith("/api/ping"):
            return "internal-ops-api"
        if path.startswith("/download") or path.startswith("/images"):
            return "file-delivery-service"
        if path.startswith("/docs") or path.startswith("/report"):
            return "knowledge-and-analytics"
        return "web-application"

    def _derive_deployment_tier(self) -> str:
        if self._current_example is None:
            return "production"
        if self._current_example.deployment_tier:
            return self._current_example.deployment_tier
        if self._current_example.queue in {"internal-api", "infra-api", "admin-api"}:
            return "internal-production"
        return "internet-facing-production"

    def _derive_detection_source(self) -> str:
        if self._current_example is None:
            return "waf"
        if self._current_example.detection_source:
            return self._current_example.detection_source
        queue = self._current_example.queue
        if "waf" in queue or "edge" in queue or "cdn" in queue:
            return "edge detection pipeline"
        if "auth" in queue:
            return "authentication anomaly detector"
        if "db" in queue:
            return "database abuse monitor"
        return "application security telemetry"

    def _derive_business_impact(self) -> str:
        if self._current_example is None:
            return "Potential security risk under investigation."
        if self._current_example.business_impact:
            return self._current_example.business_impact
        service = self._derive_service()
        severity = self._current_example.severity
        if severity in {"critical", "high"}:
            return (
                f"Active exploitation against {service} could expose sensitive data, "
                "disrupt business workflows, or create follow-on compromise."
            )
        if severity == "medium":
            return (
                f"Improper handling in {service} could enable limited compromise or "
                "customer-facing abuse if not contained."
            )
        return f"Observed traffic appears low risk for {service}, but still requires verification."

    def _derive_customer_impact(self) -> str:
        if self._current_example is None:
            return "No customer impact assessed."
        if self._current_example.customer_impact:
            return self._current_example.customer_impact
        if self._current_example.vulnerability_type == "safe":
            return "No direct customer impact expected."
        if self._current_example.severity == "critical":
            return "Potential account compromise or sensitive data exposure for active users."
        if self._current_example.severity == "high":
            return "Potential service abuse or unauthorized backend access impacting customer trust."
        return "Potential localized impact if malicious input is rendered or stored."

    def _derive_handoff(self) -> str:
        if self._current_example is None:
            return "Awaiting analyst triage."
        if self._current_example.analyst_handoff:
            return self._current_example.analyst_handoff
        return (
            "Confirm the vulnerability family, severity, and safest immediate response. "
            "Use investigation artifacts to justify containment."
        )

    def _build_observation(
        self,
        reward: Optional[Reward] = None,
        done: Optional[bool] = None,
    ) -> Observation:
        if self._current_example is None:
            raise RuntimeError("Environment must be reset() before requesting an observation.")

        task_definition = TASKS[self._state.current_task]
        remaining = max(0, self._state.max_steps - self._state.steps_taken)
        active_reward = reward or self._state.last_reward
        is_done = self._state.completed if done is None else done
        return Observation(
            task=self._state.current_task,
            task_label=TASK_LABELS[self._state.current_task],
            request_id=self._current_example.request_id,
            queue=self._current_example.queue,
            title=self._current_example.title,
            service=self._derive_service(),
            deployment_tier=self._derive_deployment_tier(),
            triage_priority=SEVERITY_TO_PRIORITY[self._current_example.severity],
            business_impact=self._derive_business_impact(),
            detection_source=self._derive_detection_source(),
            customer_impact=self._derive_customer_impact(),
            analyst_handoff=self._derive_handoff(),
            method=self._current_example.method,
            path=self._current_example.path,
            headers=self._current_example.headers,
            query_params=self._current_example.query_params,
            body=self._current_example.body,
            source_ip=self._current_example.source_ip,
            user_agent=self._current_example.user_agent,
            instructions=task_definition.instructions,
            steps_taken=self._state.steps_taken,
            remaining_steps=remaining,
            available_artifacts=[
                artifact_name
                for artifact_name in self._current_example.artifacts
                if artifact_name not in self._state.revealed_artifacts
            ],
            collected_artifacts=list(self._state.revealed_artifacts),
            evidence_log=list(self._state.evidence_log),
            available_action_types=list(ALL_ACTIONS),
            allowed_vulnerabilities=["safe", "xss", "sql_injection", "command_injection", "path_traversal"],
            allowed_severities=["none", "low", "medium", "high", "critical"],
            allowed_actions=["allow", "block", "sanitize", "monitor"],
            reward=active_reward.score if active_reward else 0.0,
            done=is_done,
            metadata={
                "reward": active_reward.model_dump() if active_reward else None,
                "info": self._info(active_reward) if active_reward else {},
            },
        )

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task: Optional[TaskName] = None,
        case_index: Optional[int] = None,
        **kwargs: object,
    ) -> Observation:
        del kwargs
        task_name = task or self._state.current_task
        task_definition = TASKS[task_name]
        if case_index is not None:
            example_index = case_index % len(self.examples)
            self._cursor_by_task[task_name] = (example_index + 1) % len(self.examples)
        elif seed is not None:
            example_index = seed % len(self.examples)
            self._cursor_by_task[task_name] = (example_index + 1) % len(self.examples)
        else:
            example_index = self._cursor_by_task[task_name] % len(self.examples)
            self._cursor_by_task[task_name] = (example_index + 1) % len(self.examples)
        self._current_example = self.examples[example_index]
        self._state = EnvironmentState(
            current_task=task_name,
            current_index=example_index,
            episode_count=self._state.episode_count + 1,
            steps_taken=0,
            step_count=0,
            max_steps=task_definition.max_steps,
            completed=False,
            last_request_id=self._current_example.request_id,
            revealed_artifacts=[],
            evidence_log=[],
            last_reward=None,
            episode_id=episode_id or str(uuid.uuid4()),
        )
        return self._build_observation(reward=None, done=False)

    def _investigation_reward(self, action_type: str) -> Reward:
        artifact_name = ACTION_TO_ARTIFACT[action_type]
        if artifact_name in self._state.revealed_artifacts:
            return Reward(
                score=clamp_open_unit_interval(0.0),
                step_score=clamp_open_unit_interval(0.0),
                terminal_score=clamp_open_unit_interval(0.0),
                investigation_score=clamp_open_unit_interval(0.0),
                decision_score=clamp_open_unit_interval(0.0),
                efficiency_score=clamp_open_unit_interval(0.0),
                safety_penalty=0.02,
                feedback=f"{artifact_name} was already reviewed; repeated inspection adds no value.",
            )

        artifact_text = self._current_example.artifacts[artifact_name]
        self._state.revealed_artifacts.append(artifact_name)
        self._state.evidence_log.append(f"{artifact_name}: {artifact_text}")

        useful = action_type in self._current_example.useful_actions
        step_score = 0.12 if useful else 0.05
        return Reward(
            score=clamp_open_unit_interval(step_score),
            step_score=clamp_open_unit_interval(step_score),
            terminal_score=clamp_open_unit_interval(0.0),
            investigation_score=clamp_open_unit_interval(step_score),
            decision_score=clamp_open_unit_interval(0.0),
            efficiency_score=clamp_open_unit_interval(0.0),
            safety_penalty=0.0,
            feedback=f"Reviewed {artifact_name}. Added analyst evidence to the case file.",
        )

    def _timeout_reward(self) -> Reward:
        return Reward(
            score=clamp_open_unit_interval(0.0),
            step_score=clamp_open_unit_interval(0.0),
            terminal_score=clamp_open_unit_interval(0.0),
            investigation_score=clamp_open_unit_interval(0.0),
            decision_score=clamp_open_unit_interval(0.0),
            efficiency_score=clamp_open_unit_interval(0.0),
            safety_penalty=0.25,
            feedback="Episode ended before a triage decision was submitted.",
        )

    def _info(self, reward: Optional[Reward]) -> Dict[str, object]:
        if self._current_example is None or reward is None:
            return {}
        info = StepInfo(
            task=self._state.current_task,
            task_label=TASK_LABELS[self._state.current_task],
            request_id=self._current_example.request_id,
            grader_name=GRADERS[self._state.current_task].name,
            steps_taken=self._state.steps_taken,
            revealed_artifacts=list(self._state.revealed_artifacts),
            ground_truth_vulnerability=self._current_example.vulnerability_type,
            ground_truth_severity=self._current_example.severity,
            ground_truth_action=self._current_example.recommended_action,
            component_scores={
                "step": reward.step_score,
                "terminal": reward.terminal_score,
                "investigation": reward.investigation_score,
                "decision": reward.decision_score,
                "efficiency": reward.efficiency_score,
                "safety_penalty": reward.safety_penalty,
            },
        )
        return info.model_dump()

    def step(
        self,
        action: Action,
        timeout_s: Optional[float] = None,
        **kwargs: object,
    ) -> Observation:
        del timeout_s, kwargs
        if self._current_example is None:
            raise RuntimeError("Environment must be reset() before step().")
        if self._state.completed:
            raise RuntimeError("Episode is complete. Call reset() to start a new case.")

        self._state.steps_taken += 1
        self._state.step_count = self._state.steps_taken

        if action.action_type == "submit_triage":
            reward = compute_reward(self._state.current_task, action, self._current_example, self._state)
            self._state.completed = True
            self._state.last_reward = reward
            return self._build_observation(reward=reward, done=True)

        reward = self._investigation_reward(action.action_type)

        if self._state.steps_taken >= self._state.max_steps:
            self._state.completed = True
            timeout_reward = self._timeout_reward()
            self._state.last_reward = timeout_reward
            return self._build_observation(reward=timeout_reward, done=True)

        self._state.last_reward = reward
        return self._build_observation(reward=reward, done=False)

    @property
    def state(self) -> EnvironmentState:
        return self._state.model_copy(deep=True)

    def get_metadata(self):
        return build_environment_metadata()
