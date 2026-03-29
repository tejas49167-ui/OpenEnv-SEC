from __future__ import annotations

from typing import Dict, Optional, Tuple

from env.data import load_examples
from env.models import Action, EnvironmentState, Observation, StepInfo, TaskName
from env.reward import GRADERS, compute_reward
from env.tasks import TASKS


class CyberVulnerabilityTriageEnvironment:
    def __init__(self, task: TaskName = "easy") -> None:
        self.examples = load_examples()
        self._cursor_by_task: Dict[TaskName, int] = {"easy": 0, "medium": 0, "hard": 0}
        self._state = EnvironmentState(current_task=task)
        self._current_example = None

    def _build_observation(self, task: TaskName, example_index: int) -> Observation:
        example = self.examples[example_index]
        task_definition = TASKS[task]
        self._current_example = example
        self._state.current_task = task
        self._state.current_index = example_index
        self._state.completed = False
        self._state.last_request_id = example.request_id
        return Observation(
            task=task,
            request_id=example.request_id,
            method=example.method,
            path=example.path,
            headers=example.headers,
            query_params=example.query_params,
            body=example.body,
            source_ip=example.source_ip,
            user_agent=example.user_agent,
            instructions=task_definition.instructions,
            allowed_vulnerabilities=["safe", "xss", "sql_injection", "command_injection", "path_traversal"],
            allowed_severities=["none", "low", "medium", "high", "critical"],
            allowed_actions=["allow", "block", "sanitize"],
        )

    def reset(self, task: Optional[TaskName] = None) -> Observation:
        task_name = task or self._state.current_task
        example_index = self._cursor_by_task[task_name] % len(self.examples)
        self._cursor_by_task[task_name] = (example_index + 1) % len(self.examples)
        self._state.episode_count += 1
        self._state.last_reward = None
        return self._build_observation(task_name, example_index)

    def step(self, action: Action) -> Tuple[Observation, "Reward", bool, Dict[str, object]]:
        if self._current_example is None:
            raise RuntimeError("Environment must be reset() before step().")

        reward = compute_reward(self._state.current_task, action, self._current_example)
        self._state.completed = True
        self._state.last_reward = reward
        observation = self._build_observation(self._state.current_task, self._state.current_index)
        self._state.completed = True
        info = StepInfo(
            task=self._state.current_task,
            request_id=self._current_example.request_id,
            ground_truth_vulnerability=self._current_example.vulnerability_type,
            ground_truth_severity=self._current_example.severity,
            ground_truth_action=self._current_example.recommended_action,
            grader_name=GRADERS[self._state.current_task].name,
            component_scores={
                "vulnerability": reward.vulnerability_score,
                "severity": reward.severity_score,
                "action": reward.action_score,
                "explanation": reward.explanation_score,
                "penalty": reward.penalty,
            },
        )
        return observation, reward, True, info.model_dump()

    def state(self) -> EnvironmentState:
        return self._state.model_copy(deep=True)

