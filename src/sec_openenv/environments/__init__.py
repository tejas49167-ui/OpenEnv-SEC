"""Environment collection namespace for Sec-OpenEnv."""

from __future__ import annotations

__all__ = [
    "CyberVulnerabilityTriageEnvironment",
    "LogAnomalyResponseEnvironment",
    "PhishingDetectionEnvironment",
]


def __getattr__(name: str):
    if name == "CyberVulnerabilityTriageEnvironment":
        from sec_openenv.environments.cyber_vulnerability_triage.environment import (
            CyberVulnerabilityTriageEnvironment,
        )

        return CyberVulnerabilityTriageEnvironment
    if name == "LogAnomalyResponseEnvironment":
        from sec_openenv.environments.log_anomaly.environment import LogAnomalyResponseEnvironment

        return LogAnomalyResponseEnvironment
    if name == "PhishingDetectionEnvironment":
        from sec_openenv.environments.phishing_detection.environment import (
            PhishingDetectionEnvironment,
        )

        return PhishingDetectionEnvironment
    raise AttributeError(f"module 'sec_openenv.environments' has no attribute {name!r}")
