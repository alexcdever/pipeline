import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.contract import validate_task


CHAIN_NAMES = ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")

# A historical derived contract: the derived token and derived_from survive only
# as a read-compatible shape for frozen history. Nothing creates them any more,
# so these fixtures are fed straight to the contract validator.
HISTORICAL_DERIVED = {
    "schema": 3,
    "task_id": "historical-derived",
    "task_type": "derived",
    "project_type": "service",
    "risk": "medium",
    "implement_plan": {"path": "implement-plan.md"},
    "allowed_paths": ["pipeline_tools/**"],
    "forbidden_paths": [".pipeline/**"],
    "non_goals": ["history stays readable"],
    "operations": [
        {
            "id": "validate",
            "kind": "validate",
            "scope": "task",
            "resources": ["pipeline_tools/core.py"],
            "resource_mode": "single",
            "acceptance_tests": ["acceptance-test-1"],
        }
    ],
    "chain": {name: ["pipeline_tools/core.py"] for name in CHAIN_NAMES},
    "acceptance_tests": [
        {
            "id": "acceptance-test-1",
            "evidence_level": 2,
            "test_ref": (
                "tests/test_derived_task_dispatch_recovery.py: "
                "DerivedTaskDispatchRecoveryTests.test_historical_derived_contracts_still_validate"
            ),
            "command_ref": (
                "python -m pytest -q tests/test_derived_task_dispatch_recovery.py "
                "-k historical_derived_contracts_still_validate"
            ),
        }
    ],
    "dependencies": ["parent-task"],
    "derived_from": {
        "task_id": "parent-task",
        "commit": "0" * 40,
        "branch": "parent-branch",
        "parent_task_type": "repair",
    },
    "required_evidence_levels": [2],
}


def historical_sheet(mutate=None) -> str:
    data = copy.deepcopy(HISTORICAL_DERIVED)
    if mutate is not None:
        mutate(data)
    return (
        "# historical derived\n<!-- Task ID: historical-derived -->\n```pipeline-contract\n"
        + json.dumps(data)
        + "\n```\n"
    )


class DerivedTaskDispatchRecoveryTests(unittest.TestCase):
    def _errors(self, mutate=None) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            sheet = Path(directory) / "historical-derived.md"
            sheet.write_text(historical_sheet(mutate), encoding="utf-8")
            return validate_task(sheet)

    def test_historical_derived_contracts_still_validate(self):
        # 1. The frozen historical shape passes the contract validator unchanged.
        self.assertEqual(self._errors(), [])

        # 2. It also passes the real `task validate` read path.
        with tempfile.TemporaryDirectory() as directory:
            sheet = Path(directory) / "historical-derived.md"
            sheet.write_text(historical_sheet(), encoding="utf-8")
            environment = dict(__import__("os").environ)
            environment.update(
                {
                    "PYTHONPATH": str(Path(__file__).resolve().parent.parent),
                    "PIPELINE_TOOLS_DISABLE_AUTO_METRICS": "1",
                }
            )
            validated = subprocess.run(
                ["python", "-m", "pipeline_tools", "task", "validate", str(sheet)],
                cwd=directory,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validated.returncode, 0, (validated.stdout, validated.stderr))

        # 3. Parent types vertical-feature and repair keep the tightened chain:
        #    a derived child may not exempt its chain with structured not_applicable.
        def exempt_chain(data):
            for name in CHAIN_NAMES:
                data["chain"][name] = {"not_applicable": True, "reason": "not part of this task"}

        for parent_type in ("vertical-feature", "repair"):
            with self.subTest(parent_task_type=parent_type):
                errors = self._errors(
                    lambda data, parent_type=parent_type: (
                        exempt_chain(data),
                        data["derived_from"].__setitem__("parent_task_type", parent_type),
                    )
                )
                self.assertTrue(errors, errors)
                self.assertTrue(
                    any("must be a non-empty array" in error for error in errors), errors
                )

        # 4. The vertical-feature parent still raises the evidence floor to 2.
        def low_evidence(data):
            data["risk"] = "low"
            data["acceptance_tests"][0]["evidence_level"] = 1
            data["required_evidence_levels"] = [1]

        vertical = self._errors(
            lambda data: (
                low_evidence(data),
                data["derived_from"].__setitem__("parent_task_type", "vertical-feature"),
            )
        )
        self.assertTrue(any("floor 2" in error for error in vertical), vertical)

        # 5. A repair parent tightens the chain but does not raise the floor;
        #    a prerequisite parent keeps both exemptions.
        repair = self._errors(
            lambda data: (
                low_evidence(data),
                data["derived_from"].__setitem__("parent_task_type", "repair"),
            )
        )
        self.assertFalse(any("floor" in error for error in repair), repair)

        prerequisite = self._errors(
            lambda data: (
                low_evidence(data),
                exempt_chain(data),
                data["derived_from"].__setitem__("parent_task_type", "prerequisite"),
            )
        )
        self.assertEqual(prerequisite, [])


if __name__ == "__main__":
    unittest.main()
