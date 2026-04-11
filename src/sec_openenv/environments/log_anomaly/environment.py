from __future__ import annotations

import uuid
from typing import Any

from sec_openenv.core.base import TaskDefinition
from sec_openenv.environments.log_anomaly.models import (
    Action,
    EnvironmentState,
    LogExample,
    Observation,
    Reward,
    build_environment_metadata,
)

TASKS = {
    "screen": TaskDefinition(
        name="screen",
        description="Quickly decide whether a log event looks suspicious.",
        instructions="Inspect the raw event and decide if it requires deeper review.",
        max_steps=3,
        required_artifacts_for_full_credit=1,
    ),
    "investigate": TaskDefinition(
        name="investigate",
        description="Gather event context and compare with baseline behavior.",
        instructions="Use supporting telemetry before deciding on severity.",
        max_steps=4,
        required_artifacts_for_full_credit=2,
    ),
    "respond": TaskDefinition(
        name="respond",
        description="Recommend the safest operational response.",
        instructions="Inspect the event, gather context, and choose a response action.",
        max_steps=5,
        required_artifacts_for_full_credit=3,
    ),
}

TASK_ALIASES = {"easy": "screen", "medium": "investigate", "hard": "respond"}

EXAMPLES = [
    LogExample(
        event_id="LOG-001",
        service="auth-api",
        raw_log='{"event":"login_failed","username":"admin","count":28,"src_ip":"203.0.113.11"}',
        label="bruteforce",
        severity="medium",
        recommended_action="monitor",
        artifacts={
            "log": "Twenty-eight failed logins for admin from one IP in six minutes.",
            "context": "No successful logins followed; attempts span multiple usernames.",
            "baseline": "This service usually sees fewer than three failed logins per IP per hour.",
        },
        useful_actions=["inspect_log", "inspect_context", "review_baseline"],
    ),
    LogExample(
        event_id="LOG-002",
        service="billing-worker",
        raw_log='{"event":"s3_copy","actor":"svc-billing","bytes_out":7340032000,"dest":"external-bucket"}',
        label="data_exfiltration",
        severity="high",
        recommended_action="page_oncall",
        artifacts={
            "log": "Large copy operation moved 7GB to an external bucket.",
            "context": "The service account normally writes only to internal analytics buckets.",
            "baseline": "Outbound transfers above 500MB are rare and usually ticketed.",
        },
        useful_actions=["inspect_log", "inspect_context", "review_baseline"],
    ),
    LogExample(
        event_id="LOG-003",
        service="ssh-gateway",
        raw_log='{"event":"sudo","user":"deploy","command":"useradd tempadmin","tty":"pts/1"}',
        label="privilege_escalation",
        severity="high",
        recommended_action="isolate_host",
        artifacts={
            "log": "A deployment account executed privileged user creation.",
            "context": "No maintenance window or approved change is linked to the session.",
            "baseline": "This host rarely sees direct sudo usage from deployment identities.",
        },
        useful_actions=["inspect_log", "inspect_context", "review_baseline"],
    ),
    LogExample(
        event_id="LOG-004",
        service="api-gateway",
        raw_log='{"event":"http_200","path":"/health","latency_ms":12}',
        label="benign",
        severity="none",
        recommended_action="ignore",
        artifacts={
            "log": "Routine health-check request with expected latency.",
            "context": "The same event appears every 30 seconds from the load balancer.",
            "baseline": "Identical heartbeat logs are part of steady-state operations.",
        },
        useful_actions=["inspect_log"],
    ),
    LogExample(
        event_id="LOG-005",
        service="vpn-gateway",
        raw_log='{"event":"login_failed","username":"finance","count":8,"country":"RU"}',
        label="bruteforce",
        severity="low",
        recommended_action="monitor",
        artifacts={
            "log": "Repeated failed logins target a privileged finance username.",
            "context": "Attempts stopped after rate-limiting and did not bypass MFA.",
            "baseline": "Cross-border attempts do occur, but clustered failures are uncommon.",
        },
        useful_actions=["inspect_log", "inspect_context"],
    ),
    LogExample(
        event_id="LOG-006",
        service="search-api",
        raw_log='{"event":"cache_warm","keys":421,"duration_ms":3421}',
        label="benign",
        severity="none",
        recommended_action="ignore",
        artifacts={
            "log": "Routine cache warm-up after deployment.",
            "context": "A deploy event occurred four minutes earlier.",
            "baseline": "Warm-up jobs run after each release.",
        },
        useful_actions=["inspect_log"],
    ),
]


class LogAnomalyEnvironment:
    slug = "log-anomaly"
    display_name = "Log Anomaly Investigation"
    domain = "detection engineering"
    supports_concurrent_sessions = False
    task_catalog = TASKS

    def __init__(self, task: str = "screen") -> None:
        task = TASK_ALIASES.get(task, task)
        self.examples = EXAMPLES
        self._state = EnvironmentState(current_task=task, max_steps=TASKS[task].max_steps)
        self._current: LogExample | None = None

    def reset(
        self,
        task: str | None = None,
        seed: int | None = None,
        case_index: int | None = None,
        **kwargs: Any,
    ) -> Observation:
        del kwargs
        task_name = TASK_ALIASES.get(
            task or self._state.current_task, task or self._state.current_task
        )
        index = (
            case_index
            if case_index is not None
            else seed
            if seed is not None
            else self._state.current_index + 1
        )
        self._current = self.examples[index % len(self.examples)]
        self._state = EnvironmentState(
            episode_id=str(uuid.uuid4()),
            current_task=task_name,
            current_index=index % len(self.examples),
            steps_taken=0,
            max_steps=TASKS[task_name].max_steps,
            completed=False,
            revealed_artifacts=[],
        )
        return self._build_observation()

    def _build_observation(self, reward: Reward | None = None, done: bool = False) -> Observation:
        return Observation(
            task=self._state.current_task,
            event_id=self._current.event_id,
            service=self._current.service,
            raw_log=self._current.raw_log,
            instructions=TASKS[self._state.current_task].instructions,
            steps_taken=self._state.steps_taken,
            remaining_steps=max(0, self._state.max_steps - self._state.steps_taken),
            available_action_types=[
                "inspect_log",
                "inspect_context",
                "review_baseline",
                "submit_triage",
            ],
            collected_artifacts=list(self._state.revealed_artifacts),
            evidence_log=[
                f"{name}: {self._current.artifacts[name]}"
                for name in self._state.revealed_artifacts
            ],
            done=done,
            reward=reward.score if reward else 0.0,
            metadata={"reward": reward.model_dump() if reward else None},
        )

    def step(self, action: Action, **kwargs: Any) -> Observation:
        del kwargs
        self._state.steps_taken += 1
        self._state.step_count = self._state.steps_taken
        if action.action_type == "submit_triage":
            score = 0.5 if action.label == self._current.label else 0.0
            if action.severity == self._current.severity:
                score += 0.25
            if action.response_action == self._current.recommended_action:
                score += 0.25
            reward = Reward(
                score=min(0.999, max(0.001, score)), feedback="Classification submitted."
            )
            self._state.completed = True
            return self._build_observation(reward=reward, done=True)
        artifact = {
            "inspect_log": "log",
            "inspect_context": "context",
            "review_baseline": "baseline",
        }[action.action_type]
        if artifact not in self._state.revealed_artifacts:
            self._state.revealed_artifacts.append(artifact)
        return self._build_observation(
            reward=Reward(score=0.1, feedback=f"Reviewed {artifact}."), done=False
        )

    @property
    def state(self) -> EnvironmentState:
        return self._state.model_copy(deep=True)

    def get_metadata(self) -> Any:
        return build_environment_metadata(len(self.examples))


LogAnomalyResponseEnvironment = LogAnomalyEnvironment
