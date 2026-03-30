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
        raw_text = " ".join(
            [
                observation.path,
                json.dumps(observation.query_params, sort_keys=True),
                observation.body,
            ]
        )
        upper_text = raw_text.upper()
        haystack = raw_text.lower()

        if "<script" in haystack or "onerror=" in haystack:
            return Action(
                vulnerability_type="xss",
                severity="high",
                response_action="sanitize",
                explanation="Script content suggests XSS and should be sanitized.",
            )
        if " OR " in upper_text or "UNION SELECT" in upper_text:
            return Action(
                vulnerability_type="sql_injection",
                severity="critical",
                response_action="block",
                explanation="Injection pattern suggests SQL injection and should be blocked.",
            )
        if ";" in raw_text:
            return Action(
                vulnerability_type="command_injection",
                severity="high",
                response_action="block",
                explanation="Command separator suggests command injection and should be blocked.",
            )
        if "../" in haystack:
            return Action(
                vulnerability_type="path_traversal",
                severity="high",
                response_action="block",
                explanation="File path traversal markers suggest an injection attempt and should be blocked.",
            )
        return Action(
            vulnerability_type="safe",
            severity="none",
            response_action="allow",
            explanation="This looks like a normal request and can be allowed.",
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
