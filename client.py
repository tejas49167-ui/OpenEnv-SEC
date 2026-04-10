from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from openenv.core.client_types import StepResult
    from openenv.core.env_client import EnvClient
    from openenv.core.env_server.types import State
except ImportError:  # pragma: no cover
    StepResult = None
    EnvClient = object
    State = object

from env.models import Action, EnvironmentState, Observation


class CyberVulnerabilityTriageEnv(EnvClient):  # type: ignore[misc]
    """Typed OpenEnv client for the cyber triage environment."""

    async def reset_task(
        self,
        task: str,
        seed: Optional[int] = None,
        case_index: Optional[int] = None,
    ):
        payload: Dict[str, Any] = {"task": task}
        if seed is not None:
            payload["seed"] = seed
        if case_index is not None:
            payload["case_index"] = case_index
        return await self.reset(**payload)

    async def inspect_payload(self):
        return await self.step(Action(action_type="inspect_payload"))

    async def decode_obfuscation(self):
        return await self.step(Action(action_type="decode_obfuscation"))

    async def review_history(self):
        return await self.step(Action(action_type="review_history"))

    async def check_source_reputation(self):
        return await self.step(Action(action_type="check_source_reputation"))

    async def inspect_asset_context(self):
        return await self.step(Action(action_type="inspect_asset_context"))

    async def consult_playbook(self):
        return await self.step(Action(action_type="consult_playbook"))

    async def submit_triage(
        self,
        vulnerability_type: str,
        severity: str,
        response_action: str,
        explanation: str,
    ):
        return await self.step(
            Action(
                action_type="submit_triage",
                vulnerability_type=vulnerability_type,
                severity=severity,
                response_action=response_action,
                explanation=explanation,
            )
        )

    def _step_payload(self, action: Action) -> Dict[str, Any]:
        return action.model_dump()

    def _parse_result(self, payload: Dict[str, Any]):
        if StepResult is None:  # pragma: no cover
            return payload
        return StepResult(
            observation=Observation(**payload["observation"]),
            reward=payload.get("reward"),
            done=payload.get("done", False),
            info=payload.get("info", {}),
        )

    def _parse_state(self, payload: Dict[str, Any]):
        if State is object:  # pragma: no cover
            return payload
        return EnvironmentState(**payload)
