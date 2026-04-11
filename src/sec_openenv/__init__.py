"""Sec-OpenEnv framework namespace."""

from __future__ import annotations

from sec_openenv.__about__ import __version__

__all__ = [
    "__version__",
    "EnvironmentDescriptor",
    "EpisodeTrace",
    "create_environment",
    "evaluate_models",
    "get_environment",
    "list_environments",
    "run_episode",
]


def __getattr__(name: str):
    if name == "EpisodeTrace":
        from sec_openenv.evaluation import EpisodeTrace

        return EpisodeTrace
    if name in {"evaluate_models", "run_episode"}:
        from sec_openenv.evaluation import evaluate_models, run_episode

        return {"evaluate_models": evaluate_models, "run_episode": run_episode}[name]
    if name in {"EnvironmentDescriptor", "create_environment", "get_environment", "list_environments"}:
        from sec_openenv.framework import (
            EnvironmentDescriptor,
            create_environment,
            get_environment,
            list_environments,
        )

        return {
            "EnvironmentDescriptor": EnvironmentDescriptor,
            "create_environment": create_environment,
            "get_environment": get_environment,
            "list_environments": list_environments,
        }[name]
    raise AttributeError(f"module 'sec_openenv' has no attribute {name!r}")
