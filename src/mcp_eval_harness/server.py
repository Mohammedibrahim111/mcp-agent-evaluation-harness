"""MCP v2 adapter for repository inspection and deterministic verification."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server import MCPServer

from .models import TaskSpec
from .verifier import DeterministicVerifier
from .workspace import SafeWorkspace


ROOT = Path(os.environ.get("MCP_EVAL_ROOT", ".")).expanduser().resolve()
server = MCPServer(
    "mcp-agent-evaluation-harness",
    instructions=(
        "Inspect the repository before proposing changes. Use verify_solution after every "
        "candidate change and report failed checks without hiding nondeterminism."
    ),
)


@server.tool()
def list_repository_files(suffix: str = "") -> list[str]:
    """List repository files in stable lexical order."""

    return SafeWorkspace(ROOT).list_files(suffix or None)


@server.tool()
def read_repository_file(path: str) -> str:
    """Read one UTF-8 repository file within the configured root."""

    return SafeWorkspace(ROOT).read_text(path)


@server.tool()
def search_repository(query: str, limit: int = 50) -> list[dict[str, object]]:
    """Search repository text with stable file and line ordering."""

    return SafeWorkspace(ROOT).search(query, limit)


@server.tool()
def verify_solution(task_file: str, workspace: str = ".") -> dict[str, object]:
    """Run a task specification and return a structured verification report."""

    root_workspace = SafeWorkspace(ROOT)
    task_path = root_workspace.resolve(task_file)
    candidate_root = root_workspace.resolve(workspace)
    report = DeterministicVerifier(candidate_root).verify(TaskSpec.from_path(task_path))
    return report.to_dict()


def run() -> None:
    server.run()


if __name__ == "__main__":
    run()
