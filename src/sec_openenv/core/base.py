from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class TaskDefinition:
    name: str
    description: str
    instructions: str
    max_steps: int
    required_artifacts_for_full_credit: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def model_dump(self) -> dict[str, Any]:
        return self.to_dict()


@dataclass(frozen=True)
class FrameworkMetadata:
    name: str
    description: str
    domain: str
    version: str
    dataset_size: int
    documentation_url: str | None = None
    tags: list[str] = field(default_factory=list)
    maturity: str = "beta"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def model_dump(self) -> dict[str, Any]:
        return self.to_dict()


class SupportsModelDump(Protocol):
    def model_dump(self) -> dict[str, Any]: ...


class SecurityEnvironment(Protocol):
    slug: str
    display_name: str
    domain: str
    supports_concurrent_sessions: bool
    task_catalog: dict[str, TaskDefinition]

    def reset(self, **kwargs: Any) -> SupportsModelDump: ...
    def step(self, action: Any, **kwargs: Any) -> SupportsModelDump: ...
    def get_metadata(self) -> Any: ...

    @property
    def state(self) -> SupportsModelDump: ...
