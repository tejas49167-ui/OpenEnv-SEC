"""Configuration path helpers for Sec-OpenEnv."""

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def openenv_manifest_path() -> Path:
    return project_root() / "configs" / "openenv" / "cyber-vulnerability-triage.yaml"


__all__ = ["project_root", "openenv_manifest_path"]
