from __future__ import annotations

from typing import Dict, Optional, Tuple

from env.data import load_examples
from env.models import TASK_LABELS, Action, EnvironmentState, Observation, Reward, StepInfo, TaskName
from env.reward import GRADERS, compute_reward
from env.scoring import clamp_open_unit_interval
from env.tasks import TASKS


ACTION_TO_ARTIFACT = {
    "inspect_payload": "payload_analysis",
    "decode_obfuscation": "decoded_input",
    "review_history": "traffic_history",
    "check_source_reputation": "source_reputation",
    "inspect_asset_context": "asset_context",
    "consult_playbook": "playbook_guidance",
}

ALL_ACTIONS = list(ACTION_TO_ARTIFACT.keys()) + ["submit_triage"]


class CyberVulnerabilityTriageEnvironment:
    def __init__(self, task: TaskName = "easy") -> None:
        self.examples = load_examples()
        self._cursor_by_task: Dict[TaskName, int] = {"easy": 0, "medium": 0, "hard": 0}
        self._state = EnvironmentState(current_task=task, max_steps=TASKS[task].max_steps)
        self._current_example = None

    def _build_observation(self) -> Observation:
        if self._current_example is None:
            raise RuntimeError("Environment must be reset() before requesting an observation.")

        task_definition = TASKS[self._state.current_task]
        remaining = max(0, self._state.max_steps - self._state.steps_taken)
        return Observation(
            task=self._state.current_task,
            task_label=TASK_LABELS[self._state.current_task],
            request_id=self._current_example.request_id,
            queue=self._current_example.queue,
            title=self._current_example.title,
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
        )

    def reset(self, task: Optional[TaskName] = None) -> Observation:
        task_name = task or self._state.current_task
        task_definition = TASKS[task_name]
        example_index = self._cursor_by_task[task_name] % len(self.examples)
        self._cursor_by_task[task_name] = (example_index + 1) % len(self.examples)
        self._current_example = self.examples[example_index]
        self._state = EnvironmentState(
            current_task=task_name,
            current_index=example_index,
            episode_count=self._state.episode_count + 1,
            steps_taken=0,
            max_steps=task_definition.max_steps,
            completed=False,
            last_request_id=self._current_example.request_id,
            revealed_artifacts=[],
            evidence_log=[],
            last_reward=None,
        )
        return self._build_observation()

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

    def _info(self, reward: Reward) -> Dict[str, object]:
        if self._current_example is None:
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

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, object]]:
        if self._current_example is None:
            raise RuntimeError("Environment must be reset() before step().")
        if self._state.completed:
            raise RuntimeError("Episode is complete. Call reset() to start a new case.")

        self._state.steps_taken += 1

        if action.action_type == "submit_triage":
            reward = compute_reward(self._state.current_task, action, self._current_example, self._state)
            self._state.completed = True
            self._state.last_reward = reward
            return self._build_observation(), reward, True, self._info(reward)

        reward = self._investigation_reward(action.action_type)

        if self._state.steps_taken >= self._state.max_steps:
            self._state.completed = True
            timeout_reward = self._timeout_reward()
            self._state.last_reward = timeout_reward
            return self._build_observation(), timeout_reward, True, self._info(timeout_reward)

        self._state.last_reward = reward
        return self._build_observation(), reward, False, self._info(reward)

    def state(self) -> EnvironmentState:
        return self._state.model_copy(deep=True)
