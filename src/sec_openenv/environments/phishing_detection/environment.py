from __future__ import annotations

import uuid
from typing import Any

from sec_openenv.core.base import TaskDefinition
from sec_openenv.environments.phishing_detection.models import (
    Action,
    EmailExample,
    EnvironmentState,
    Observation,
    Reward,
    build_environment_metadata,
)

TASKS = {
    "screen": TaskDefinition(
        name="screen",
        description="Quickly decide whether an email is suspicious.",
        instructions="Use one or two checks to classify the email.",
        max_steps=3,
        required_artifacts_for_full_credit=1,
    ),
    "investigate": TaskDefinition(
        name="investigate",
        description="Gather evidence from sender, links, and tenant history.",
        instructions="Inspect multiple artifacts before deciding on severity.",
        max_steps=4,
        required_artifacts_for_full_credit=2,
    ),
    "respond": TaskDefinition(
        name="respond",
        description="Classify the message and recommend the safest response.",
        instructions="Investigate the message, determine severity, and choose an operational response.",
        max_steps=5,
        required_artifacts_for_full_credit=3,
    ),
}

EXAMPLES = [
    EmailExample(
        email_id="MAIL-001",
        sender="it-support@micr0soft-help.com",
        subject="Password reset required today",
        body="Please sign in to keep your mailbox active.",
        urls=["https://login-microsoft-help.example/reset"],
        attachments=[],
        label="credential_harvest",
        severity="high",
        recommended_action="block_domain",
        artifacts={
            "headers": "Return-Path and DKIM domain do not match Microsoft branding.",
            "links": "Displayed domain imitates Microsoft but resolves to a newly registered host.",
            "history": "Ten similar messages hit the tenant in the last hour.",
        },
        useful_actions=["inspect_headers", "inspect_links", "review_history"],
    ),
    EmailExample(
        email_id="MAIL-002",
        sender="ceo@company-finance.co",
        subject="Urgent wire transfer",
        body="Need an immediate transfer before the board call. Reply only to this thread.",
        urls=[],
        attachments=[],
        label="business_email_compromise",
        severity="high",
        recommended_action="escalate",
        artifacts={
            "headers": "Display name matches the CEO, but the sender domain is external.",
            "links": "No links included.",
            "history": "No prior relationship exists with this sender and finance staff received similar variants.",
        },
        useful_actions=["inspect_headers", "review_history"],
    ),
    EmailExample(
        email_id="MAIL-003",
        sender="docs@company.com",
        subject="Quarterly handbook update",
        body="Updated handbook is attached for review.",
        urls=["https://intranet.company.com/handbook"],
        attachments=["Employee-Handbook.pdf"],
        label="benign",
        severity="none",
        recommended_action="allow",
        artifacts={
            "headers": "SPF, DKIM, and DMARC align with the corporate domain.",
            "links": "Link points to the internal intranet domain.",
            "history": "Similar messages are sent quarterly from the same sender.",
        },
        useful_actions=["inspect_headers", "inspect_links"],
    ),
    EmailExample(
        email_id="MAIL-004",
        sender="security-alerts@paypa1-support.co",
        subject="Account limitation notice",
        body="Open the attached HTML to restore your account access.",
        urls=[],
        attachments=["restore_access.html"],
        label="phishing",
        severity="medium",
        recommended_action="quarantine",
        artifacts={
            "headers": "Sender domain uses a character substitution and failed DMARC.",
            "links": "No inline links. The HTML attachment contains a credential form.",
            "history": "Three recipients reported similar messages in the shared mailbox.",
        },
        useful_actions=["inspect_headers", "inspect_links", "review_history"],
    ),
    EmailExample(
        email_id="MAIL-005",
        sender="vendor@trusted-partner.com",
        subject="Invoice portal reminder",
        body="Monthly portal reminder for open invoices.",
        urls=["https://portal.trusted-partner.com/invoices"],
        attachments=[],
        label="benign",
        severity="none",
        recommended_action="allow",
        artifacts={
            "headers": "Sender aligns with a known vendor profile.",
            "links": "Domain matches the vendor allowlist.",
            "history": "Similar reminders are received every month.",
        },
        useful_actions=["inspect_headers"],
    ),
    EmailExample(
        email_id="MAIL-006",
        sender="benefits@companny-hr.com",
        subject="Open enrollment action needed",
        body="Use the secure link to update payroll details.",
        urls=["https://companny-hr-benefits.example/update"],
        attachments=[],
        label="credential_harvest",
        severity="medium",
        recommended_action="quarantine",
        artifacts={
            "headers": "Brand impersonation with a misspelled corporate domain.",
            "links": "Link targets a non-corporate domain hosting a fake login form.",
            "history": "Campaign overlaps with a known HR-themed lure cluster.",
        },
        useful_actions=["inspect_headers", "inspect_links", "review_history"],
    ),
]


class PhishingDetectionEnvironment:
    slug = "phishing-detection"
    display_name = "Phishing Detection"
    domain = "email security triage"
    supports_concurrent_sessions = False
    task_catalog = TASKS

    def __init__(self, task: str = "screen") -> None:
        self.examples = EXAMPLES
        self._state = EnvironmentState(current_task=task, max_steps=TASKS[task].max_steps)
        self._current: EmailExample | None = None

    def reset(
        self,
        task: str | None = None,
        seed: int | None = None,
        case_index: int | None = None,
        **kwargs: Any,
    ) -> Observation:
        del kwargs
        task_name = task or self._state.current_task
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
            email_id=self._current.email_id,
            sender=self._current.sender,
            subject=self._current.subject,
            body=self._current.body,
            urls=self._current.urls,
            attachments=self._current.attachments,
            instructions=TASKS[self._state.current_task].instructions,
            steps_taken=self._state.steps_taken,
            remaining_steps=max(0, self._state.max_steps - self._state.steps_taken),
            available_action_types=[
                "inspect_headers",
                "inspect_links",
                "review_history",
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
            "inspect_headers": "headers",
            "inspect_links": "links",
            "review_history": "history",
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
