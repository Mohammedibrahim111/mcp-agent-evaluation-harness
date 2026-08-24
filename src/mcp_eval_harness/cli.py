"""Command-line interface for the evaluation harness."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .models import TaskSpec
from .verifier import DeterministicVerifier


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    verify = subcommands.add_parser("verify", help="run one deterministic task")
    verify.add_argument("task_file")
    verify.add_argument("workspace")
    subcommands.add_parser("serve", help="start the MCP server over stdio")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "serve":
        from .server import run

        run()
        return 0
    spec = TaskSpec.from_path(arguments.task_file)
    report = DeterministicVerifier(arguments.workspace).verify(spec)
    print(report.to_json())
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
