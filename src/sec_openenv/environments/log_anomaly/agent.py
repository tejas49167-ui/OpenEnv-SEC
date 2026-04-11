from __future__ import annotations

from typing import Any

from sec_openenv.environments.log_anomaly.models import Action, Observation


class LogAnomalyBaselineAgent:
    def __init__(self, client: Any = None, model_name: str = "gpt-4o-mini") -> None:
        self.client = client
        self.model_name = model_name

    def decide(self, observation: Observation) -> Action:
        if "log" not in observation.collected_artifacts and observation.remaining_steps > 1:
            return Action(action_type="inspect_log")
        if (
            observation.task != "screen"
            and "context" not in observation.collected_artifacts
            and observation.remaining_steps > 1
        ):
            return Action(action_type="inspect_context")
        if (
            observation.task == "respond"
            and "baseline" not in observation.collected_artifacts
            and observation.remaining_steps > 1
        ):
            return Action(action_type="review_baseline")
        combined = f"{observation.raw_log} {' '.join(observation.evidence_log)}".lower()
        if "external-bucket" in combined or "bytes_out" in combined:
            label, severity, response = "data_exfiltration", "high", "page_oncall"
        elif "useradd tempadmin" in combined or "sudo" in combined:
            label, severity, response = "privilege_escalation", "high", "isolate_host"
        elif "login_failed" in combined:
            severity = "medium" if '"count":28' in combined else "low"
            label, response = "bruteforce", "monitor"
        else:
            label, severity, response = "benign", "none", "ignore"
        return Action(
            action_type="submit_triage",
            label=label,
            severity=severity,
            response_action=response,
            explanation="Observed log content and surrounding evidence support this operational triage.",
        )
