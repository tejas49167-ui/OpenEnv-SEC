from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from sec_openenv.core.loader import load_object


@dataclass(frozen=True)
class EnvironmentDescriptor:
    slug: str
    display_name: str
    package: str
    environment_entrypoint: str
    action_model_entrypoint: str
    default_agent_entrypoint: str
    server_entrypoint: str
    description: str
    domain: str
    maturity: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def load_environment_class(self) -> type[Any]:
        return load_object(self.environment_entrypoint)

    def load_action_model(self) -> type[Any]:
        return load_object(self.action_model_entrypoint)

    def load_default_agent(self) -> type[Any]:
        return load_object(self.default_agent_entrypoint)

    def load_server(self) -> Any:
        return load_object(self.server_entrypoint)

    def create_environment(self, **kwargs: Any) -> Any:
        return self.load_environment_class()(**kwargs)


_ENVIRONMENTS: dict[str, EnvironmentDescriptor] = {
    "cyber-vulnerability-triage": EnvironmentDescriptor(
        slug="cyber-vulnerability-triage",
        display_name="Cyber Vulnerability Triage",
        package="sec_openenv.environments.cyber_vulnerability_triage",
        environment_entrypoint=(
            "sec_openenv.environments.cyber_vulnerability_triage.environment:"
            "CyberVulnerabilityTriageEnvironment"
        ),
        action_model_entrypoint="sec_openenv.environments.cyber_vulnerability_triage.models:Action",
        default_agent_entrypoint=(
            "sec_openenv.environments.cyber_vulnerability_triage.agent:CyberTriageBaselineAgent"
        ),
        server_entrypoint="sec_openenv.environments.cyber_vulnerability_triage.server:app",
        description=(
            "Multi-step application security triage over suspicious HTTP requests with "
            "deterministic grading."
        ),
        domain="application security incident triage",
        maturity="beta",
        tags=["triage", "web-security", "benchmark"],
    ),
    "log-anomaly": EnvironmentDescriptor(
        slug="log-anomaly",
        display_name="Log Anomaly Investigation",
        package="sec_openenv.environments.log_anomaly",
        environment_entrypoint=(
            "sec_openenv.environments.log_anomaly.environment:LogAnomalyEnvironment"
        ),
        action_model_entrypoint="sec_openenv.environments.log_anomaly.models:Action",
        default_agent_entrypoint="sec_openenv.environments.log_anomaly.agent:LogAnomalyBaselineAgent",
        server_entrypoint="sec_openenv.environments.log_anomaly.server:app",
        description=(
            "Operational security environment for log triage, evidence gathering, and "
            "response recommendation."
        ),
        domain="detection engineering",
        maturity="alpha",
        tags=["logs", "anomaly", "soc"],
    ),
}


def list_environments() -> list[EnvironmentDescriptor]:
    return [_ENVIRONMENTS[slug] for slug in sorted(_ENVIRONMENTS)]


def get_environment(slug: str) -> EnvironmentDescriptor:
    if slug not in _ENVIRONMENTS:
        known = ", ".join(sorted(_ENVIRONMENTS))
        raise KeyError(f"Unknown environment '{slug}'. Known environments: {known}")
    return _ENVIRONMENTS[slug]


def create_environment(slug: str, **kwargs: Any) -> Any:
    return get_environment(slug).create_environment(**kwargs)
