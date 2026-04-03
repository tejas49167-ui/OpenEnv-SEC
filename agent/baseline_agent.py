from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI

from env.models import Action, Observation


class BaselineTriageAgent:
    def __init__(self, client: Optional[OpenAI] = None, model_name: str = "gpt-4o-mini") -> None:
        self.client = client
        self.model_name = model_name

    def _prompt(self, observation: Observation) -> str:
        return (
            "You are a senior web-security analyst operating inside a deterministic triage environment.\n"
            "Return strict JSON with keys: action_type, vulnerability_type, severity, response_action, explanation.\n"
            "For non-submit actions, set vulnerability_type, severity, and response_action to null.\n"
            f"Task: {observation.task}\n"
            f"Instructions: {observation.instructions}\n"
            f"Alert: {observation.title}\n"
            f"Queue: {observation.queue}\n"
            f"Method: {observation.method}\n"
            f"Path: {observation.path}\n"
            f"Headers: {json.dumps(observation.headers, sort_keys=True)}\n"
            f"Query Params: {json.dumps(observation.query_params, sort_keys=True)}\n"
            f"Body: {observation.body}\n"
            f"Collected evidence: {json.dumps(observation.evidence_log, ensure_ascii=True)}\n"
            f"Collected artifacts: {json.dumps(observation.collected_artifacts)}\n"
            f"Remaining steps: {observation.remaining_steps}\n"
            "Available action types: inspect_payload, decode_obfuscation, review_history, "
            "check_source_reputation, inspect_asset_context, consult_playbook, submit_triage.\n"
            "When enough evidence exists, submit a final triage."
        )

    def _extract_json(self, content: str) -> Dict[str, Any]:
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if "\n" in content:
                content = content.split("\n", 1)[1]
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError("No JSON object found in model response.")
        return json.loads(content[start : end + 1])

    def _detect(self, observation: Observation) -> Dict[str, str]:
        request_text = " ".join(
            [
                observation.path,
                json.dumps(observation.query_params, sort_keys=True),
                observation.body,
                observation.title,
            ]
        )
        evidence_text = " ".join(observation.evidence_log)
        combined_text = f"{request_text} {evidence_text}"
        lower = combined_text.lower()
        request_lower = request_text.lower()

        if any(token in lower for token in ["<script", "onerror=", "script>", "javascript:"]):
            return {
                "vulnerability_type": "xss",
                "severity": "medium",
                "response_action": "sanitize"
                if any(token in lower for token in ["encoded", "&#x3c", "%3cscript"])
                else "block",
            }
        if re.search(r"(?i)union\s+select", combined_text) or re.search(
            r"(?i)(['\"].{0,12}\bor\b.{0,12}=)|(/\*\*/or/\*\*/)|sqlmap",
            combined_text,
        ):
            return {
                "vulnerability_type": "sql_injection",
                "severity": "critical",
                "response_action": "block",
            }
        if re.search(r"(?i)(;|&&)\s*(ls|whoami|cat|id)\b", combined_text) or (
            "command injection" in lower and any(token in request_lower for token in ["/api/ping", "/api/archive"])
        ):
            return {
                "vulnerability_type": "command_injection",
                "severity": "high",
                "response_action": "block",
            }
        if any(token in lower for token in ["../", "..%2f", "etc/passwd", "auth.log", "path traversal"]):
            return {
                "vulnerability_type": "path_traversal",
                "severity": "high",
                "response_action": "block",
            }
        return {
            "vulnerability_type": "safe",
            "severity": "none",
            "response_action": "allow",
        }

    def _preferred_action_sequence(self, observation: Observation, prediction: Dict[str, str]) -> List[str]:
        sequence = ["inspect_payload"]
        raw = " ".join([json.dumps(observation.query_params, sort_keys=True), observation.body]).lower()

        if any(token in raw for token in ["%3c", "&#x3c", "%20%26%26", "..%2f", "/**/"]):
            sequence.append("decode_obfuscation")
        if observation.task in {"medium", "hard"}:
            sequence.append("review_history")
        if observation.task == "hard":
            sequence.append("inspect_asset_context")
            if prediction["vulnerability_type"] in {"sql_injection", "path_traversal"}:
                sequence.append("check_source_reputation")
            sequence.append("consult_playbook")
        elif observation.task == "medium":
            sequence.append("consult_playbook")
        return sequence

    def _build_explanation(self, prediction: Dict[str, str]) -> str:
        vulnerability = prediction["vulnerability_type"]
        response = prediction["response_action"]
        severity = prediction["severity"]
        if vulnerability == "safe":
            return "Evidence points to normal application usage with no exploit indicators, so this request is safe and should be allowed."
        if vulnerability == "xss":
            return f"Payload evidence indicates XSS-style script injection, the severity is {severity}, and the safest response is to {response} the request."
        if vulnerability == "sql_injection":
            return f"Request contains SQL injection indicators tied to authentication or data access, making this {severity} severity and a clear {response} decision."
        if vulnerability == "command_injection":
            return f"Input shows command injection behavior with shell execution markers, so this is {severity} severity and should be {response}ed."
        return f"Decoded path manipulation indicates path traversal, which is {severity} severity and should be {response}ed to protect sensitive files."

    def _heuristic_action(self, observation: Observation) -> Action:
        prediction = self._detect(observation)
        planned_actions = self._preferred_action_sequence(observation, prediction)

        for action_type in planned_actions:
            artifact = {
                "inspect_payload": "payload_analysis",
                "decode_obfuscation": "decoded_input",
                "review_history": "traffic_history",
                "check_source_reputation": "source_reputation",
                "inspect_asset_context": "asset_context",
                "consult_playbook": "playbook_guidance",
            }[action_type]
            if artifact not in observation.collected_artifacts and observation.remaining_steps > 1:
                return Action(action_type=action_type, explanation="")

        return Action(
            action_type="submit_triage",
            vulnerability_type=prediction["vulnerability_type"],
            severity=prediction["severity"],
            response_action=prediction["response_action"],
            explanation=self._build_explanation(prediction),
        )

    def _parse_response(self, content: str) -> Action:
        payload = self._extract_json(content)
        return Action(**payload)

    def decide(self, observation: Observation) -> Action:
        if not self.client:
            return self._heuristic_action(observation)

        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=self._prompt(observation),
                temperature=0,
            )
            return self._parse_response(response.output_text)
        except Exception:
            return self._heuristic_action(observation)
