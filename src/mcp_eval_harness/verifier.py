"""Repeatable verification for coding-agent task environments."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

from .models import CheckResult, TaskSpec, VerificationReport
from .workspace import SafeWorkspace


class DeterministicVerifier:
    """Evaluate file requirements and command output under a fixed environment."""

    def __init__(self, workspace: str | Path):
        self.workspace = SafeWorkspace(workspace)

    def verify(self, spec: TaskSpec) -> VerificationReport:
        checks: list[CheckResult] = []
        checks.extend(self._check_required_files(spec))
        checks.extend(self._check_patterns(spec.required_patterns, required=True))
        checks.extend(self._check_patterns(spec.forbidden_patterns, required=False))

        exit_codes: list[int] = []
        outputs: list[tuple[str, str]] = []
        for _ in range(spec.repeat_count):
            try:
                completed = subprocess.run(
                    list(spec.command),
                    cwd=self.workspace.root,
                    env=self._controlled_environment(),
                    capture_output=True,
                    text=True,
                    timeout=spec.timeout_seconds,
                    check=False,
                )
                exit_codes.append(completed.returncode)
                outputs.append((completed.stdout, completed.stderr))
            except subprocess.TimeoutExpired as error:
                exit_codes.append(124)
                outputs.append((error.stdout or "", error.stderr or "verification timed out"))

        commands_passed = all(code == 0 for code in exit_codes)
        deterministic = len(set(zip(exit_codes, outputs))) == 1
        checks.append(CheckResult("command_exit", commands_passed, f"exit codes: {exit_codes}"))
        checks.append(
            CheckResult(
                "deterministic_output",
                deterministic,
                "all repeated runs matched" if deterministic else "repeated runs differed",
            )
        )
        passed = all(check.passed for check in checks)
        stdout, stderr = outputs[-1] if outputs else ("", "")
        return VerificationReport(
            task_id=spec.task_id,
            passed=passed,
            checks=checks,
            command_exit_codes=exit_codes,
            deterministic_output=deterministic,
            stdout=stdout,
            stderr=stderr,
        )

    def _check_required_files(self, spec: TaskSpec) -> list[CheckResult]:
        results = []
        for relative_path in spec.required_files:
            path = self.workspace.resolve(relative_path)
            results.append(
                CheckResult(
                    f"required_file:{relative_path}",
                    path.is_file(),
                    "present" if path.is_file() else "missing",
                )
            )
        return results

    def _check_patterns(
        self, patterns_by_file: dict[str, tuple[str, ...]], required: bool
    ) -> list[CheckResult]:
        results = []
        for relative_path, patterns in sorted(patterns_by_file.items()):
            try:
                text = self.workspace.read_text(relative_path)
            except FileNotFoundError:
                text = ""
            for pattern in patterns:
                found = pattern in text
                passed = found if required else not found
                rule = "required_pattern" if required else "forbidden_pattern"
                detail = "found" if found else "not found"
                results.append(CheckResult(f"{rule}:{relative_path}:{pattern}", passed, detail))
        return results

    @staticmethod
    def _controlled_environment() -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(
            {
                "LC_ALL": "C.UTF-8",
                "LANG": "C.UTF-8",
                "TZ": "UTC",
                "PYTHONHASHSEED": "0",
                "NO_COLOR": "1",
            }
        )
        return environment
