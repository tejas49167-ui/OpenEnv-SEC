from __future__ import annotations

from typing import Any

from sec_openenv.environments.phishing_detection.models import Action, Observation


class PhishingBaselineAgent:
    def __init__(self, client: Any = None, model_name: str = "gpt-4o-mini") -> None:
        self.client = client
        self.model_name = model_name

    def decide(self, observation: Observation) -> Action:
        if (
            "inspect_headers" not in observation.collected_artifacts
            and observation.remaining_steps > 1
        ):
            return Action(action_type="inspect_headers")
        if (
            observation.urls
            and "inspect_links" not in observation.collected_artifacts
            and observation.remaining_steps > 1
        ):
            return Action(action_type="inspect_links")
        if (
            observation.task != "screen"
            and "review_history" not in observation.collected_artifacts
            and observation.remaining_steps > 1
        ):
            return Action(action_type="review_history")
        combined = f"{observation.sender} {observation.subject} {observation.body} {' '.join(observation.evidence_log)}".lower()
        if "ceo" in combined and "wire" in combined:
            label, severity, response = "business_email_compromise", "high", "escalate"
        elif (
            "fake login" in combined
            or "microsoft" in combined
            or "paypa1" in combined
            or "misspelled" in combined
        ):
            label = (
                "credential_harvest"
                if "login" in combined or "microsoft" in combined
                else "phishing"
            )
            severity = "high" if "newly registered" in combined else "medium"
            response = "block_domain" if "newly registered" in combined else "quarantine"
        else:
            label, severity, response = "benign", "none", "allow"
        return Action(
            action_type="submit_triage",
            label=label,
            severity=severity,
            response_action=response,
            explanation="Evidence from sender identity, links, and history supports this classification.",
        )
