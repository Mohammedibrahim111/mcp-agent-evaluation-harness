"""Typed data models used by the verifier."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class TaskSpec:
    """A validated, deterministic verification contract."""

    task_id: str
    required_files: tuple[str, ...]
    required_patterns: dict[str, tuple[str, ...]]
    forbidden_patterns: dict[str, tuple[str, ...]]
    command: tuple[str, ...]
    timeout_seconds: int = 10
    repeat_count: int = 2

    @classmethod
    def from_path(cls, path: str | Path) -> "TaskSpec":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskSpec":
        task_id = str(data.get("task_id", "")).strip()
        command = tuple(str(part) for part in data.get("command", []))
        timeout = int(data.get("timeout_seconds", 10))
        repeats = int(data.get("repeat_count", 2))
        if not task_id:
            raise ValueError("task_id is required")
        if not command:
            raise ValueError("command must contain at least one argument")
        if not 1 <= timeout <= 120:
            raise ValueError("timeout_seconds must be between 1 and 120")
        if not 2 <= repeats <= 5:
            raise ValueError("repeat_count must be between 2 and 5")
        return cls(
            task_id=task_id,
            required_files=tuple(str(item) for item in data.get("required_files", [])),
            required_patterns={
                str(name): tuple(str(pattern) for pattern in patterns)
                for name, patterns in data.get("required_patterns", {}).items()
            },
            forbidden_patterns={
                str(name): tuple(str(pattern) for pattern in patterns)
                for name, patterns in data.get("forbidden_patterns", {}).items()
            },
            command=command,
            timeout_seconds=timeout,
            repeat_count=repeats,
        )


@dataclass(frozen=True)
class CheckResult:
    """The result of one verification rule."""

    name: str
    passed: bool
    detail: str


@dataclass
class VerificationReport:
    """The complete, serializable evaluation result."""

    task_id: str
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    command_exit_codes: list[int] = field(default_factory=list)
    deterministic_output: bool = False
    stdout: str = ""
    stderr: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
