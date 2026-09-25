import json
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.planning import append_progress


class ProgressTests(unittest.TestCase):
    def test_each_role_appends_to_its_own_jsonl_without_touching_task_sheet(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sheet = root / "docs" / "tasks" / "demo.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text("frozen", encoding="utf-8")

            executor = append_progress(root, "demo", "executor", {"event": "started"})
            reviewer = append_progress(root, "demo", "reviewer", {"event": "checked"})
            main = append_progress(root, "demo", "main", {"event": "decided"})

            self.assertEqual(executor.name, "executor-progress.jsonl")
            self.assertEqual(reviewer.name, "reviewer-progress.jsonl")
            self.assertEqual(main.name, "main-progress.jsonl")
            self.assertEqual(len(executor.read_text(encoding="utf-8").splitlines()), 1)
            value = json.loads(executor.read_text(encoding="utf-8"))
            self.assertEqual(value["task_id"], "demo")
            self.assertEqual(value["role"], "executor")
            self.assertEqual(sheet.read_text(encoding="utf-8"), "frozen")

    def test_progress_rejects_invalid_identity_and_sensitive_values(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for role in ("invalid", "EXECUTOR"):
                with self.assertRaises(ValueError):
                    append_progress(root, "demo", role, {"event": "bad"})
            with self.assertRaises(ValueError):
                append_progress(root, "../demo", "executor", {"event": "bad"})
            with self.assertRaises(ValueError):
                append_progress(root, "demo", "executor", {"credentials": {"password": "secret"}})
            with self.assertRaises(ValueError):
                append_progress(root, "demo", "executor", {"task_id": "other"})

    def test_progress_rejects_symlinked_task_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".pipeline").mkdir()
            (root / ".pipeline" / "linked").symlink_to(root.parent, target_is_directory=True)
            with self.assertRaises(ValueError):
                append_progress(root, "linked", "executor", {"event": "escape"})


if __name__ == "__main__":
    unittest.main()
