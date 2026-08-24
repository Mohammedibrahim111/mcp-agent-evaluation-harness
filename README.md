# MCP Agent Evaluation Harness

A compact reference project for evaluating coding agents that use Model Context Protocol tools. The harness gives an agent controlled repository access, runs repeatable checks, compares repeated executions, and returns a structured verification report.

## What the project demonstrates

- An MCP server with repository listing, reading, searching, and verification tools
- Root-confined file access with traversal protection
- Deterministic command execution with fixed locale, timezone, and Python hash seed
- Required and forbidden code-pattern checks
- Repeat-run comparison for nondeterminism detection
- Golden reference material for a reproducible bug-fixing task
- Standard-library unit tests and a continuous integration workflow

## Architecture

```text
MCP client or coding agent
          |
          v
Repository MCP tools
          |
          v
SafeWorkspace boundary
          |
          v
DeterministicVerifier
          |
          v
Structured VerificationReport
```

The core verifier has no third-party dependency. The MCP adapter uses the official Python SDK v2.

## Quick start

Run the unit tests.

```bash
python -m unittest discover -s tests -v
```

Run the included evaluation task.

```bash
PYTHONPATH=src python -m mcp_eval_harness.cli verify \
  examples/rounding-bug/task.json \
  examples/rounding-bug/workspace
```

Install the MCP adapter and start the stdio server.

```bash
python -m pip install -e ".[mcp]"
mcp-eval serve
```

## MCP tools

| Tool | Purpose |
| --- | --- |
| `list_repository_files` | Return a stable, sorted file list under the configured root |
| `read_repository_file` | Read one UTF-8 file while blocking path traversal |
| `search_repository` | Find literal text with deterministic ordering and result limits |
| `verify_solution` | Run the task specification and return a structured report |

## Task specification

Each task is JSON and declares the files, code requirements, verification command, timeout, and repeat count.

```json
{
  "task_id": "decimal-rounding-fix",
  "required_files": ["calculator.py", "test_calculator.py"],
  "required_patterns": {"calculator.py": ["Decimal", "ROUND_HALF_UP"]},
  "forbidden_patterns": {"calculator.py": ["round("]},
  "command": ["python", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"],
  "timeout_seconds": 10,
  "repeat_count": 2
}
```

## Security boundary

The path checks protect the configured repository root. The command verifier is designed for trusted local task definitions. Run untrusted candidate code inside a container or another operating-system sandbox.

## Author

Mohammed Ibrahim Sadiq

## License

MIT
