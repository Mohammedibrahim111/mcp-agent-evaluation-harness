from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _bootstrap import add_src_to_path

add_src_to_path()

from mcp_eval_harness.workspace import SafeWorkspace


class SafeWorkspaceTests(unittest.TestCase):
    def test_lists_and_searches_in_stable_order(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "b.py").write_text("needle = 2\n", encoding="utf-8")
            (root / "a.py").write_text("needle = 1\n", encoding="utf-8")
            workspace = SafeWorkspace(root)
            self.assertEqual(workspace.list_files(".py"), ["a.py", "b.py"])
            self.assertEqual(
                [match["path"] for match in workspace.search("needle")],
                ["a.py", "b.py"],
            )

    def test_blocks_parent_traversal(self):
        with TemporaryDirectory() as directory:
            workspace = SafeWorkspace(directory)
            with self.assertRaises(ValueError):
                workspace.resolve("../outside.txt")


if __name__ == "__main__":
    unittest.main()
