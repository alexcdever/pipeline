import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.planning import detect_fact_conflicts, gate_facts_for_planning, validate_facts_model


class PlanningFactsConflictTests(unittest.TestCase):
    def valid_model(self):
        return {
            "schema": 1,
            "planning_run_id": "run-1",
            "facts": [
                {"id": "req-1", "category": "requirement", "entity_id": "scope", "value": "safe", "source_id": "plan", "path": "implement-plan.md"},
                {"id": "proj-1", "category": "project", "entity_id": "runtime", "value": "python", "source_id": "repo", "path": "pipeline_tools/planning.py"},
            ],
            "assumptions": [{"id": "assume-1", "source_id": "plan", "status": "open"}],
            "unknowns": [{"id": "unknown-1", "source_id": "plan", "status": "resolved"}],
            "conflicts": [],
            "non_goals": ["本任务不扩展用户可见功能"],
            "decision_blockers": [],
        }

    def test_facts_are_classified_with_sources_and_safe_identity(self):
        result = detect_fact_conflicts(self.valid_model(), planning_run_id="run-1")
        self.assertEqual(result["status"], "pass")
        self.assertEqual({item["category"] for item in result["facts"]}, {"requirement", "project"})
        self.assertEqual(result["planning_run_id"], "run-1")
        self.assertEqual(validate_facts_model(self.valid_model()), [])

    def test_conflicts_block_planning_and_preserve_decision_records(self):
        model = self.valid_model()
        model["facts"].append({"id": "req-2", "category": "requirement", "entity_id": "scope", "value": "unsafe", "source_id": "other", "path": "implement-plan.md"})
        result = gate_facts_for_planning(model, planning_run_id="run-1")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["planning_allowed"])
        self.assertTrue(result["decision_required"])
        self.assertEqual(result["conflicts"][0]["status"], "blocking")
        self.assertIn("obtain product decision", result["conflicts"][0]["next_actions"])

    def test_decision_blocker_status_semantics_are_explicit_and_fail_closed(self):
        for status, blocked in (("blocking", True), ("resolved", False), ("non_blocking", False), ("unknown", True), (None, True)):
            model = self.valid_model()
            blocker = {"id": "decision-1"}
            if status is not None:
                blocker["status"] = status
            model["decision_blockers"] = [blocker]
            result = gate_facts_for_planning(model, planning_run_id="run-1")
            self.assertEqual(result["status"] == "blocked", blocked, status)
            self.assertEqual(result["planning_allowed"], not blocked, status)
            self.assertIn("decision-1", {item.get("id") for item in result["decision_blockers"]})

    def test_invalid_facts_and_unauthorized_resolution_are_rejected(self):
        model = self.valid_model()
        model["facts"][0]["source_id"] = ""
        model["facts"][0]["path"] = "../outside"
        model["facts"].append({"id": "req-1", "category": "requirement", "source_id": "plan"})
        model["unknowns"][0] = {"id": "unknown-1", "source_id": "plan", "status": "resolved", "resolution": "auto"}
        errors = validate_facts_model(model)
        self.assertTrue(any("source" in error for error in errors))
        self.assertTrue(any("unsafe" in error for error in errors))
        self.assertTrue(any("duplicate" in error for error in errors))
        self.assertTrue(any("unauthorized decision fields" in error for error in errors))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "facts.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            completed = subprocess.run([sys.executable, "-m", "pipeline_tools", "planning", "facts-gate-planning", str(path)], capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn('"planning_allowed": false', completed.stdout)

    def test_non_goals_must_be_recorded_as_explicit_sentences(self):
        missing = self.valid_model()
        del missing["non_goals"]
        self.assertTrue(any("non_goals" in error for error in validate_facts_model(missing)))
        self.assertEqual(gate_facts_for_planning(missing)["status"], "blocked")

        empty = dict(self.valid_model(), non_goals=[])
        self.assertTrue(any("non_goals" in error for error in validate_facts_model(empty)))
        self.assertFalse(gate_facts_for_planning(empty)["planning_allowed"])

        blank = dict(self.valid_model(), non_goals=["   "])
        self.assertTrue(any("non_goals" in error for error in validate_facts_model(blank)))

        explicit = dict(self.valid_model(), non_goals=["本项目没有非目标；范围仅限已记录需求"])
        self.assertEqual(validate_facts_model(explicit), [])
        self.assertEqual(gate_facts_for_planning(explicit)["status"], "pass")


if __name__ == "__main__":
    unittest.main()
