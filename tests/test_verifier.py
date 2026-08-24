from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _bootstrap import add_src_to_path

add_src_to_path()

from mcp_eval_harness.models import TaskSpec
from mcp_eval_harness.verifier import DeterministicVerifier


class DeterministicVerifierTests(unittest.TestCase):
    def test_passes_repeatable_command_and_patterns(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "solution.py").write_text("print('stable')\n", encoding="utf-8")
            spec = TaskSpec.from_dict(
                {
                    "task_id": "stable-test",
                    "required_files": ["solution.py"],
                    "required_patterns": {"solution.py": ["stable"]},
                    "forbidden_patterns": {"solution.py": ["eval("]},
                    "command": ["python", "solution.py"],
                    "repeat_count": 2,
                }
            )
            report = DeterministicVerifier(root).verify(spec)
            self.assertTrue(report.passed)
            self.assertTrue(report.deterministic_output)
            self.assertEqual(report.command_exit_codes, [0, 0])

    def test_rejects_forbidden_pattern(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "solution.py").write_text("eval('1 + 1')\n", encoding="utf-8")
            spec = TaskSpec.from_dict(
                {
                    "task_id": "unsafe-test",
                    "forbidden_patterns": {"solution.py": ["eval("]},
                    "command": ["python", "-c", "print('done')"],
                    "repeat_count": 2,
                }
            )
            report = DeterministicVerifier(root).verify(spec)
            self.assertFalse(report.passed)


if __name__ == "__main__":
    unittest.main()
