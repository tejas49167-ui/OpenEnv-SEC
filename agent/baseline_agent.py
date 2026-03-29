from __future__ import annotations

import json
import os
from typing import Any, Dict

from openai import OpenAI

from env.models import Action, Observation


class BaselineTriageAgent:
    def __init__(self) -> None:
        self.api_base_url = os.getenv("API_BASE_URL")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.hf_token = os.getenv("HF_TOKEN", "local-fallback-token")
        self.client = OpenAI(base_url=self.api_base_url, api_key=self.hf_token)

    def _prompt(self, observation: Observation) -> str:
        return (
            "You are a web security triage agent.\n"
            f"Task: {observation.task}\n"
            f"Instructions: {observation.instructions}\n"
            "Return strict JSON with keys: vulnerability_type, severity, response_action, explanation.\n"
            f"Method: {observation.method}\n"
            f"Path: {observation.path}\n"
            f"Headers: {json.dumps(observation.headers, sort_keys=True)}\n"
            f"Query Params: {json.dumps(observation.query_params, sort_keys=True)}\n"
            f"Body: {observation.body}\n"
            "Use one of the allowed values exactly."
        )

    def _heuristic_action(self, observation: Observation) -> Action:
        haystack = " ".join(
            [
                observation.path,
                json.dumps(observation.query_params, sort_keys=True),
                observation.body,
                json.dumps(observation.headers, sort_keys=True),
            ]
        ).lower()

        if any(token in haystack for token in ["<script", "onerror=", "javascript:"]):
            severity = "high" if "<script" in haystack else "medium"
            explanation = (
                "Reflected script payload suggests XSS and should be sanitized before rendering."
                if "<script" in haystack
                else "Stored HTML onerror payload suggests XSS and should be sanitized before storage."
            )
            return Action(
                vulnerability_type="xss",
                severity=severity,
                response_action="sanitize",
                explanation=explanation,
            )
        if any(token in haystack for token in [" union select ", "' or '1'='1", "sqlmap", " or "]):
            return Action(
                vulnerability_type="sql_injection",
                severity="critical",
                response_action="block",
                explanation="SQL injection payload suggests authentication bypass or exfiltration and should be blocked.",
            )
        if any(token in haystack for token in ["&&", ";", "|", "whoami", "/etc/passwd", "cat /etc/passwd"]):
            severity = "critical" if "/etc/passwd" in haystack else "high"
            explanation = (
                "Shell separator payload targets passwd and indicates command injection against backend execution."
                if severity == "critical"
                else "Shell chaining with whoami indicates command injection against backend execution."
            )
            return Action(
                vulnerability_type="command_injection",
                severity=severity,
                response_action="block",
                explanation=explanation,
            )
        if any(token in haystack for token in ["../", "..%2f", "..\\"]):
            encoded = "..%2f" in haystack
            return Action(
                vulnerability_type="path_traversal",
                severity="medium" if encoded else "high",
                response_action="block",
                explanation=(
                    "Encoded traversal attempts to read log files outside the intended directory."
                    if encoded
                    else "Path traversal markers indicate access to sensitive files outside the intended directory."
                ),
            )
        return Action(
            vulnerability_type="safe",
            severity="none",
            response_action="allow",
            explanation="This looks like a normal safe request with expected application behavior.",
        )

    def _parse_response(self, content: str) -> Action:
        payload: Dict[str, Any] = json.loads(content)
        return Action(**payload)

    def decide(self, observation: Observation) -> Action:
        if not self.api_base_url:
            return self._heuristic_action(observation)

        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=self._prompt(observation),
                temperature=0,
            )
            content = response.output_text
            return self._parse_response(content)
        except Exception:
            return self._heuristic_action(observation)
