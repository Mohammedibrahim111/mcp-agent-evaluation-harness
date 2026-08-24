"""Root-confined repository access for MCP tools."""

from __future__ import annotations

from pathlib import Path


class SafeWorkspace:
    """Expose deterministic read-only operations under one trusted root."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("workspace root must be a directory")

    def resolve(self, relative_path: str | Path) -> Path:
        candidate = (self.root / relative_path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError("path escapes the configured workspace")
        return candidate

    def list_files(self, suffix: str | None = None) -> list[str]:
        files = []
        for path in self.root.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            relative = path.relative_to(self.root).as_posix()
            if suffix is None or relative.endswith(suffix):
                files.append(relative)
        return sorted(files)

    def read_text(self, relative_path: str | Path, max_bytes: int = 200_000) -> str:
        path = self.resolve(relative_path)
        if not path.is_file():
            raise FileNotFoundError(str(relative_path))
        if path.stat().st_size > max_bytes:
            raise ValueError(f"file exceeds the {max_bytes}-byte read limit")
        return path.read_text(encoding="utf-8")

    def search(self, query: str, limit: int = 50) -> list[dict[str, object]]:
        if not query:
            raise ValueError("query must not be empty")
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")
        matches: list[dict[str, object]] = []
        for relative_path in self.list_files():
            try:
                lines = self.read_text(relative_path).splitlines()
            except (UnicodeDecodeError, ValueError):
                continue
            for line_number, line in enumerate(lines, start=1):
                if query in line:
                    matches.append(
                        {"path": relative_path, "line": line_number, "text": line.strip()}
                    )
                    if len(matches) == limit:
                        return matches
        return matches
