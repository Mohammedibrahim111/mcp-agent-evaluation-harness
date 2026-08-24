from pathlib import Path
import sys


def add_src_to_path() -> None:
    source = str(Path(__file__).resolve().parents[1] / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
