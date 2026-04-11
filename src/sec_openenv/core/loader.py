from __future__ import annotations

from importlib import import_module
from typing import Any


def load_object(entrypoint: str) -> Any:
    """Load an object from a ``module:attribute`` entrypoint string."""

    module_name, _, attribute = entrypoint.partition(":")
    if not module_name or not attribute:
        raise ValueError(f"Invalid entrypoint: {entrypoint}")
    module = import_module(module_name)
    loaded: Any = module
    for part in attribute.split("."):
        loaded = getattr(loaded, part)
    return loaded
