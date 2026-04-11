from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EnvironmentDescriptor:
    """Metadata describing an installable Sec-OpenEnv environment module."""

    slug: str
    display_name: str
    package: str
    module: str
    server_entrypoint: str
    description: str
    maturity: str


_ENVIRONMENTS: Dict[str, EnvironmentDescriptor] = {
    "cyber-vulnerability-triage": EnvironmentDescriptor(
        slug="cyber-vulnerability-triage",
        display_name="Cyber Vulnerability Triage",
        package="cyber_vulnerability_triage",
        module="sec_openenv.environments.cyber_vulnerability_triage",
        server_entrypoint="server.app:app",
        description=(
            "Deterministic, multi-step web security alert triage environment for "
            "benchmarking, experimentation, and training."
        ),
        maturity="beta",
    )
}


def list_environments() -> List[EnvironmentDescriptor]:
    """Return all environment descriptors registered in this repository."""

    return list(_ENVIRONMENTS.values())


def get_environment(slug: str) -> EnvironmentDescriptor:
    """Look up a registered environment by slug."""

    return _ENVIRONMENTS[slug]
