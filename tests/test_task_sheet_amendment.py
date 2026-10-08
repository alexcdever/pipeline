import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline_tools.core import (
    amend_task_sheet,
    evidence_revision_status,
    freeze_check,
    task_sheet_revision,
)
from pipeline_tools.planning import compare_task_plan_contract
from pipeline_tools.reconcile import reconcile_task

TASK_ID = "demo"
CHAIN_NAMES = ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")
PY = sys.executable


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    )


def run_cli(args, cwd):
    env = {**os.environ, "PIPELINE_TOOLS_DISABLE_AUTO_METRICS": "1", "PYTHONPATH": str(ROOT)}
    return subprocess.run(
        [PY, "-m", "pipeline_tools", *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=120
    )


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_exact(path, text):
    """Write bytes without Windows newline translation so hashes stay reproducible."""
    Path(path).write_bytes(text.encode("utf-8"))


class TaskSheetAmendmentTests(unittest.TestCase):
    """Task sheet amendment classification, recording, and evidence binding."""

    def _contract(self, task_id=TASK_ID, **overrides):
        contract = {
            "schema": 4,
            "task_id": task_id,
            "task_type": "repair",
            "project_type": "service",
            "risk": "medium",
            "goal": {"path": "docs/goal.md"},
            "allowed_paths": ["pipeline_tools/**", "tests/**", "docs/tasks/**"],
            "forbidden_paths": ["docs/goal.md"],
            "non_goals": ["must not rewrite history"],
            "operations": [
                {
                    "id": "op-core",
                    "kind": "repair",
                    "scope": "core",
                    "resources": ["pipeline_tools/core.py"],
                    "resource_mode": "single",
                    "acceptance_tests": ["acceptance-test-1"],
                },
                {
                    "id": "op-tests",
                    "kind": "repair",
                    "scope": "tests",
                    "resources": ["tests/test_task_sheet_amendment.py"],
                    "resource_mode": "single",
                    "acceptance_tests": ["acceptance-test-2"],
                },
            ],
            "chain": {name: ["pipeline_tools/core.py"] for name in CHAIN_NAMES},
            "acceptance_tests": [
                {
                    "id": "acceptance-test-1",
                    "evidence_level": 2,
                    "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amendment_is_allowed_after_executor_evidence",
                    "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence",
                },
                {
                    "id": "acceptance-test-2",
                    "evidence_level": 2,
                    "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_identity_fields_are_not_amendable_and_dependencies_are",
                    "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable",
                },
            ],
            "dependencies": [],
            "required_evidence_levels": [2],
            "assumptions": [],
            "unknowns": [],
        }
        contract.update(overrides)
        return contract

    def _sheet_text(self, contract, prose="契约说明：初版"):
        return (
            f"# 任务单 {contract['task_id']}\n\n"
            f"<!-- Task ID: {contract['task_id']} -->\n\n"
            f"{prose}\n\n"
            "```pipeline-contract\n" + json.dumps(contract, indent=2, ensure_ascii=True) + "\n```\n"
        )

    def _frozen_repo(self, contract=None, extra_sheets=()):
        """Create a committed repo whose task sheet has a recorded revision 1."""
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
        root = Path(directory)
        git(root, "init", "-q")
        git(root, "config", "user.email", "test@example.invalid")
        git(root, "config", "user.name", "Test")
        (root / "docs" / "tasks").mkdir(parents=True)
        (root / "docs" / "goal.md").write_text("# goal\n", encoding="utf-8")
        (root / "pipeline_tools").mkdir()
        (root / "pipeline_tools" / "core.py").write_text("# core\n", encoding="utf-8")
        sheet = root / "docs" / "tasks" / f"{TASK_ID}.md"
        write_exact(sheet, self._sheet_text(contract or self._contract()))
        for name, value in extra_sheets:
            write_exact(root / "docs" / "tasks" / f"{name}.md", value)
        git(root, "add", ".")
        git(root, "commit", "-qm", "freeze")
        head = git(root, "rev-parse", "HEAD").stdout.strip()
        errors = freeze_check(root, head, task_sheet=sheet)
        self.assertEqual(errors, [], errors)
        self.assertEqual(task_sheet_revision(root, TASK_ID), (1, digest(sheet)))
        return root, sheet, head

    def _amend(self, root, sheet, contract, **kwargs):
        text = self._sheet_text(contract, kwargs.pop("prose", "契约说明：初版"))
        self.last_sheet_text = text
        write_exact(sheet, text)
        return amend_task_sheet(root, TASK_ID, **kwargs)

    def _acceptance_result(self, observed_at, revision, baseline, acceptance_ids=("acceptance-test-1", "acceptance-test-2")):
        return {
            "schema": 1,
            "task_id": TASK_ID,
            "role": "executor",
            "status": "pass",
            "exit_code": 0,
            "sheet_revision": revision,
            "sheet_sha256": baseline,
            "observed_at_commit": observed_at,
            "acceptance": [
                {"id": item, "status": "pass", "exit_code": 0, "evidence_refs": ["executor-result.json"]}
                for item in acceptance_ids
            ],
            "unverified": [],
        }

    def test_amendment_is_allowed_after_executor_evidence(self):
        root, sheet, head = self._frozen_repo()
        revision, baseline = task_sheet_revision(root, TASK_ID)
        evidence = root / ".pipeline" / TASK_ID
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "executor-result.json").write_text(
            json.dumps(self._acceptance_result(head, revision, baseline)), encoding="utf-8"
        )
        git(root, "add", ".pipeline")
        git(root, "commit", "-qm", "executor evidence")
        head = git(root, "rev-parse", "HEAD").stdout.strip()
        git(root, "worktree", "add", "-b", TASK_ID, f".worktrees/{TASK_ID}", head)
        worktrees_before = git(root, "worktree", "list", "--porcelain").stdout
        evidence_before = {path.name: path.read_bytes() for path in evidence.iterdir()}

        value = self._amend(
            root, sheet, self._contract(),
            prose="契约说明：执行证据产生后修订散文",
            reason="clarify the design prose after the executor stage",
            requested_by="executor",
            feedback_ref="executor-result.json",
        )

        self.assertEqual(value["status"], "pass", value)
        self.assertEqual(value["revision"], 2)
        self.assertEqual(value["previous_revision"], 1)
        self.assertFalse(value["verification_surface_changed"])
        self.assertFalse(value["loosened"])
        # The same implementation worktree and the same evidence directory stay in use.
        self.assertEqual(git(root, "worktree", "list", "--porcelain").stdout, worktrees_before)
        self.assertTrue((root / f".worktrees/{TASK_ID}" / "docs" / "tasks" / f"{TASK_ID}.md").is_file())
        written = {path.name: path.read_bytes() for path in evidence.iterdir()}
        self.assertEqual(
            sorted(set(written) - set(evidence_before)), ["amendments.json"], written
        )
        for name, content in evidence_before.items():
            self.assertEqual(written[name], content, name)
        self.assertEqual(
            sorted(path.name for path in (root / ".pipeline").iterdir()), ["demo"]
        )
        # The amended revision becomes the freeze baseline, so the task continues.
        errors = freeze_check(root, head, task_sheet=sheet)
        self.assertEqual([error for error in errors if "task sheet changed after freeze" in error], [], errors)
        git(root, "add", "docs/tasks")
        git(root, "commit", "-qm", "amend prose")
        self.assertEqual(task_sheet_revision(root, TASK_ID), (2, digest(sheet)))

    def test_identity_fields_are_not_amendable_and_dependencies_are(self):
        fingerprint = {
            "task_id": self._contract(task_id="other-task"),
            "task_type": self._contract(task_type="vertical-feature"),
            "schema": {
                key: value for key, value in self._contract(goal=None, schema=3).items() if value is not None
            },
            "derived_from": self._contract(
                derived_from={
                    "task_id": "parent-task",
                    "commit": "0" * 40,
                    "branch": "main",
                    "parent_task_type": "repair",
                }
            ),
        }
        fingerprint["schema"]["implement_plan"] = {"path": "docs/goal.md"}
        dependency = self._sheet_text(self._contract(task_id="dep-alpha"))
        for field in ("task_id", "task_type", "schema", "derived_from"):
            with self.subTest(field=field):
                root, sheet, _head = self._frozen_repo()
                before = digest(sheet)
                mutated = self._sheet_text(fingerprint[field])
                write_exact(sheet, mutated)
                value = amend_task_sheet(root, TASK_ID, reason=f"attempt to revise {field}")
                self.assertEqual(value["status"], "blocked", value)
                self.assertTrue(
                    any(field in error and "not amendable" in error for error in value["errors"]),
                    value["errors"],
                )
                self.assertFalse((root / ".pipeline" / TASK_ID / "amendments.json").exists())
                self.assertEqual(task_sheet_revision(root, TASK_ID), (1, before))
                self.assertEqual(sheet.read_text(encoding="utf-8"), mutated)
                write_exact(sheet, self._sheet_text(self._contract()))
                self.assertEqual(digest(sheet), before)

        root, sheet, _head = self._frozen_repo(extra_sheets=(("dep-alpha", dependency),))
        added = self._amend(
            root, sheet, self._contract(dependencies=["dep-alpha"]),
            reason="add the dependency declared by the plan",
        )
        self.assertEqual(added["status"], "pass", added)
        self.assertEqual(added["changes"]["dependencies"], {"added": ["dep-alpha"], "removed": []})
        self.assertFalse(added["loosened"])
        self.assertFalse(added["verification_surface_changed"])
        removed = self._amend(
            root, sheet, self._contract(),
            reason="the dependency was completed by another route",
        )
        self.assertEqual(removed["status"], "pass", removed)
        self.assertEqual(removed["changes"]["dependencies"], {"added": [], "removed": ["dep-alpha"]})
        self.assertIsNone(removed["adjudication_ref"])

    def test_verification_surface_and_loosening_are_classified_independently(self):
        # (a) prose only: neither criterion fires.
        root, sheet, _head = self._frozen_repo()
        prose = self._amend(
            root, sheet, self._contract(),
            prose="契约说明：只改散文", reason="clarify the prose",
        )
        self.assertEqual(prose["status"], "pass", prose)
        self.assertFalse(prose["verification_surface_changed"])
        self.assertFalse(prose["loosened"])

        # (b) tightened acceptance tests: the verification surface changed, nothing loosened.
        tightened = self._contract()
        tightened["acceptance_tests"][0]["evidence_level"] = 3
        tightened["acceptance_tests"].append(dict(tightened["acceptance_tests"][1], id="acceptance-test-3"))
        tightened["operations"][0]["acceptance_tests"] = ["acceptance-test-1", "acceptance-test-3"]
        strict = self._amend(root, sheet, tightened, reason="tighten the acceptance evidence level")
        self.assertEqual(strict["status"], "pass", strict)
        self.assertTrue(strict["verification_surface_changed"])
        self.assertFalse(strict["loosened"])
        self.assertEqual(strict["changes"]["acceptance_tests"]["added"], ["acceptance-test-3"])

        # (c) a wider allowed_paths list is loosening: rejected without an adjudication.
        widened = self._contract()
        widened["allowed_paths"] = [*widened["allowed_paths"], "references/**"]
        rejected = self._amend(root, sheet, widened, reason="widen the allowed paths")
        self.assertEqual(rejected["status"], "blocked", rejected)
        self.assertTrue(any("adjudication" in error for error in rejected["errors"]), rejected["errors"])
        accepted = self._amend(
            root, sheet, widened, reason="widen the allowed paths", adjudication="docs/decisions/widening.md",
        )
        self.assertEqual(accepted["status"], "pass", accepted)
        self.assertTrue(accepted["verification_surface_changed"])
        self.assertTrue(accepted["loosened"])
        self.assertEqual(accepted["adjudication_ref"], "docs/decisions/widening.md")

        # (d) deleting an acceptance test is loosening and needs an adjudication.
        deleted = self._contract()
        deleted["acceptance_tests"] = [deleted["acceptance_tests"][0]]
        deleted["operations"] = [deleted["operations"][0]]
        refused = self._amend(root, sheet, deleted, reason="drop the second acceptance test")
        self.assertEqual(refused["status"], "blocked", refused)
        self.assertTrue(any("adjudication" in error for error in refused["errors"]), refused["errors"])
        permitted = self._amend(
            root, sheet, deleted, reason="drop the second acceptance test",
            adjudication="docs/decisions/drop-acceptance-test-2.md",
        )
        self.assertEqual(permitted["status"], "pass", permitted)
        self.assertTrue(permitted["loosened"])
        self.assertEqual(permitted["changes"]["acceptance_tests"]["removed"], ["acceptance-test-2"])

    def test_amend_rejects_missing_or_cyclic_dependencies(self):
        dependency = self._sheet_text(self._contract(task_id="dep-alpha"))
        cyclic = self._sheet_text(self._contract(task_id="dep-beta", dependencies=[TASK_ID]))
        archived = self._sheet_text(self._contract(task_id="dep-gamma"))
        root, sheet, _head = self._frozen_repo(
            extra_sheets=(("dep-alpha", dependency), ("dep-beta", cyclic))
        )
        (root / ".pipeline" / "archive").mkdir(parents=True, exist_ok=True)
        write_exact(root / ".pipeline" / "archive" / "dep-gamma.md", archived)

        missing = self._amend(
            root, sheet, self._contract(dependencies=["no-such-task"]),
            reason="depend on a task that does not exist",
        )
        self.assertEqual(missing["status"], "blocked", missing)
        self.assertTrue(any("no-such-task" in error for error in missing["errors"]), missing["errors"])
        self.assertFalse((root / ".pipeline" / TASK_ID / "amendments.json").exists())

        cycle = self._amend(
            root, sheet, self._contract(dependencies=["dep-beta"]),
            reason="depend on a task that already depends on this one",
        )
        self.assertEqual(cycle["status"], "blocked", cycle)
        self.assertTrue(any("cycle" in error for error in cycle["errors"]), cycle["errors"])
        self.assertFalse((root / ".pipeline" / TASK_ID / "amendments.json").exists())
        self.assertEqual(digest(sheet), hashlib.sha256(self.last_sheet_text.encode("utf-8")).hexdigest())

        for identifier in ("dep-alpha", "dep-gamma"):
            with self.subTest(dependency=identifier):
                legal = self._amend(
                    root, sheet, self._contract(dependencies=[identifier]),
                    reason=f"declare the {identifier} dependency",
                )
                self.assertEqual(legal["status"], "pass", legal)
                self.assertEqual(legal["changes"]["dependencies"]["added"], [identifier])

    def test_evidence_validity_tracks_sheet_revision(self):
        root, sheet, head = self._frozen_repo()
        revision, baseline = task_sheet_revision(root, TASK_ID)
        records = {
            "executor-report.md": {
                "schema": 2,
                "sheet_revision": revision,
                "sheet_sha256": baseline,
                "observed_at_commit": head,
                "acceptance": [{"id": "acceptance-test-1"}],
            }
        }
        contract = self._contract()

        fresh = evidence_revision_status(root, TASK_ID, contract, records)
        self.assertEqual((fresh["sheet_revision"], fresh["stale"]), (1, False), fresh)
        self.assertEqual(fresh["records"]["executor-report.md"]["reasons"], [])

        # HEAD moving on with a commit outside the verified resources keeps evidence valid.
        (root / "docs" / "notes.md").write_text("unrelated\n", encoding="utf-8")
        git(root, "add", "docs/notes.md")
        git(root, "commit", "-qm", "unrelated docs")
        moved = evidence_revision_status(root, TASK_ID, contract, records)
        self.assertFalse(moved["records"]["executor-report.md"]["stale"], moved)
        self.assertNotEqual(moved["head"], head)

        # A change to a verified resource invalidates it.
        (root / "pipeline_tools" / "core.py").write_text("# core changed\n", encoding="utf-8")
        git(root, "add", "pipeline_tools/core.py")
        git(root, "commit", "-qm", "change the verified resource")
        touched = evidence_revision_status(root, TASK_ID, contract, records)
        self.assertTrue(touched["records"]["executor-report.md"]["stale"], touched)
        self.assertTrue(
            any("pipeline_tools/core.py" in reason for reason in touched["errors"]), touched["errors"]
        )

        # A new sheet revision invalidates evidence produced against the previous one.
        amended = self._amend(
            root, sheet, self._contract(),
            prose="契约说明：证据判据改为绑定修订版本", reason="clarify the prose after evidence",
        )
        self.assertEqual(amended["status"], "pass", amended)
        stale = evidence_revision_status(root, TASK_ID, self._contract(), records)
        self.assertTrue(stale["records"]["executor-report.md"]["stale"], stale)
        self.assertTrue(
            any(
                "produced against task sheet revision 1" in reason and "current revision is 2" in reason
                for reason in stale["errors"]
            ),
            stale["errors"],
        )
        self.assertEqual(task_sheet_revision(root, TASK_ID)[0], 2)

    def test_amendment_record_is_append_only_and_structured(self):
        root, sheet, _head = self._frozen_repo()
        revision, baseline = task_sheet_revision(root, TASK_ID)
        path = root / ".pipeline" / TASK_ID / "amendments.json"

        tightened = self._contract()
        tightened["acceptance_tests"][0]["evidence_level"] = 3
        tightened["acceptance_tests"].append(dict(tightened["acceptance_tests"][1], id="acceptance-test-3"))
        tightened["operations"][0]["acceptance_tests"] = ["acceptance-test-1", "acceptance-test-3"]
        first = self._amend(root, sheet, tightened, reason="tighten acceptance evidence")
        self.assertEqual(first["status"], "pass", first)
        after_first = path.read_text(encoding="utf-8")

        loosened = self._contract()
        loosened["acceptance_tests"] = [
            dict(loosened["acceptance_tests"][0], test_ref="tests/test_x.py")
        ]
        loosened["operations"] = [loosened["operations"][0]]
        second = self._amend(
            root, sheet, loosened, reason="narrow the acceptance set",
            adjudication="docs/decisions/narrowing.md",
        )
        self.assertEqual(second["status"], "pass", second)
        after_second = path.read_text(encoding="utf-8")

        document = json.loads(after_second)
        self.assertEqual(document["schema"], 1)
        self.assertEqual(document["task_id"], TASK_ID)
        self.assertEqual([item["revision"] for item in document["revisions"]], [2, 3])
        # Append-only: every byte recorded before the new revision is untouched.
        self.assertTrue(after_second.startswith(after_first[: after_first.rindex("\n]}\n")]))
        before_lines = after_first.splitlines()
        after_lines = after_second.splitlines()
        self.assertEqual(before_lines[:2], after_lines[:2])
        self.assertEqual(after_lines[2], ",")
        self.assertEqual(
            after_lines[3], json.dumps(document["revisions"][1], ensure_ascii=True, sort_keys=True)
        )
        self.assertEqual(after_lines[4], "]}")

        required = (
            "revision", "at", "by", "requested_by", "feedback_ref", "reason", "adjudication_ref",
            "previous_sheet_sha256", "sheet_sha256", "verification_surface_changed", "loosened",
            "changes", "sheet_contract",
        )
        entries = document["revisions"]
        for entry in entries:
            self.assertEqual(set(required).issubset(entry), True, entry)
            self.assertEqual(entry["by"], "main-agent")
            self.assertEqual(entry["requested_by"], "main-agent")
            datetime.fromisoformat(entry["at"])
        self.assertEqual(entries[0]["previous_sheet_sha256"], baseline)
        self.assertEqual(entries[0]["sheet_sha256"], entries[1]["previous_sheet_sha256"])
        self.assertEqual(entries[1]["sheet_sha256"], digest(sheet))
        self.assertEqual(entries[1]["adjudication_ref"], "docs/decisions/narrowing.md")
        self.assertEqual(
            entries[0]["changes"]["acceptance_tests"]["added"], ["acceptance-test-3"]
        )
        self.assertEqual(entries[0]["changes"]["acceptance_tests"]["modified"][0]["id"], "acceptance-test-1")
        self.assertEqual(
            entries[1]["changes"]["acceptance_tests"]["removed"], ["acceptance-test-2", "acceptance-test-3"]
        )
        self.assertTrue(entries[1]["loosened"])
        self.assertEqual(revision, 1)
        self.assertEqual(task_sheet_revision(root, TASK_ID)[0], 3)

    def test_plan_contract_consistency_uses_latest_revision(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        git(root, "init", "-q")
        git(root, "config", "user.email", "test@example.invalid")
        git(root, "config", "user.name", "Test")
        (root / "docs" / "tasks").mkdir(parents=True)
        (root / "docs").mkdir(exist_ok=True)
        plan_path = root / "docs" / "goal.md"
        plan_path.write_text("stable goal\n", encoding="utf-8")
        plan_digest = digest(plan_path)
        acceptance = [
            {
                "id": "acceptance-test-1",
                "evidence_level": 2,
                "test_ref": "tests/test_x.py",
                "command_ref": "python -m unittest",
            }
        ]
        operation = {
            "id": "op", "kind": "validate", "scope": "task",
            "resources": ["pipeline_tools/core.py"], "resource_mode": "single",
            "acceptance_tests": ["acceptance-test-1"],
        }
        chain_value = {name: {"not_applicable": True, "reason": "no reference"} for name in CHAIN_NAMES}
        plan = {
            "schema": 1,
            "non_goals": ["本任务不扩展范围"],
            "requirements": ["req"],
            "resources": ["pipeline_tools/core.py", "tests/test_x.py"],
            "operations": [operation],
            "acceptance_tests": acceptance,
            "tasks": [
                {
                    "id": TASK_ID,
                    "type": "prerequisite",
                    "requirements": ["req"],
                    "resources": ["pipeline_tools/core.py", "tests/test_x.py"],
                    "operations": ["op"],
                    "chain": chain_value,
                    "depends_on": [],
                }
            ],
        }
        contract = {
            "schema": 4,
            "task_id": TASK_ID,
            "task_type": "prerequisite",
            "project_type": "service",
            "risk": "medium",
            "goal": {"path": "docs/goal.md", "sha256": plan_digest, "planning_run_id": "run-1"},
            "non_goals": ["本任务不扩展范围"],
            "allowed_paths": ["pipeline_tools/core.py", "tests/test_x.py"],
            "forbidden_paths": ["docs/goal.md"],
            "non_user_completion_reason": "prerequisite task produces enabling artifacts",
            "requirements": ["req"],
            "resources": ["pipeline_tools/core.py", "tests/test_x.py"],
            "operations": [dict(operation)],
            "chain": chain_value,
            "acceptance_tests": acceptance,
            "dependencies": [],
            "required_evidence_levels": [2],
        }
        (root / "pipeline_tools").mkdir()
        (root / "pipeline_tools" / "core.py").write_text("# core\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests" / "test_x.py").write_text("# tests\n", encoding="utf-8")
        write_exact(root / "docs" / "tasks" / "dep-x.md", self._sheet_text(self._contract(task_id="dep-x")))
        sheet = root / "docs" / "tasks" / f"{TASK_ID}.md"
        write_exact(sheet, self._sheet_text(contract))
        git(root, "add", ".")
        git(root, "commit", "-qm", "freeze")
        head = git(root, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(freeze_check(root, head, task_sheet=sheet), [])

        matching = compare_task_plan_contract(plan, sheet, root=root)
        self.assertEqual(matching["status"], "pass", matching)
        self.assertEqual(matching["sheet_revision"], 1)
        self.assertFalse(matching["revised_after_planning"])

        amended = self._amend(
            root, sheet, dict(contract, dependencies=["dep-x"]), reason="declare the dependency"
        )
        self.assertEqual(amended["status"], "pass", amended)

        revised = compare_task_plan_contract(plan, sheet, root=root)
        self.assertEqual(revised["status"], "fail")
        self.assertEqual(revised["sheet_revision"], 2)
        self.assertTrue(revised["revised_after_planning"])
        conflicts = [item for item in revised["conflicts"] if item["field"] == "dependencies"]
        self.assertEqual(len(conflicts), 1, revised["conflicts"])
        self.assertTrue(conflicts[0]["revised_after_planning"])
        self.assertIn("revised after planning", conflicts[0]["reason"])
        self.assertNotEqual(conflicts[0]["reason"], "dependencies differs between task-plan and task sheet")
        self.assertEqual(revised["next_actions"], ["re-plan against the latest task sheet revision"])

    def test_amend_requires_main_agent_role_and_adjudication_for_loosening(self):
        root, sheet, _head = self._frozen_repo()
        loosened = self._contract()
        loosened["acceptance_tests"] = [loosened["acceptance_tests"][0]]
        loosened["operations"] = [loosened["operations"][0]]

        written = self._sheet_text(loosened)
        for role in ("executor", "reviewer"):
            with self.subTest(role=role):
                write_exact(sheet, written)
                before = digest(sheet)
                value = amend_task_sheet(root, TASK_ID, reason="attempt a role violation", role=role)
                self.assertEqual(value["status"], "blocked", value)
                self.assertFalse((root / ".pipeline" / TASK_ID / "amendments.json").exists())
                self.assertEqual(digest(sheet), before)
                self.assertEqual(task_sheet_revision(root, TASK_ID)[0], 1)
                cli = run_cli(
                    [
                        "--format", "json", "task", "amend", str(root),
                        "--task-id", TASK_ID, "--reason", "attempt a role violation", "--role", role,
                    ],
                    root,
                )
                self.assertEqual(cli.returncode, 3, cli.stderr)
                payload = json.loads(cli.stdout)
                self.assertEqual(payload["command"], "task.amend")
                self.assertEqual(payload["status"], "blocked")
                self.assertFalse((root / ".pipeline" / TASK_ID / "amendments.json").exists())

        refused = amend_task_sheet(root, TASK_ID, reason="drop an acceptance test")
        self.assertEqual(refused["status"], "blocked", refused)
        self.assertTrue(any("adjudication" in error for error in refused["errors"]), refused["errors"])
        self.assertFalse((root / ".pipeline" / TASK_ID / "amendments.json").exists())

        accepted = amend_task_sheet(
            root, TASK_ID, reason="drop an acceptance test",
            adjudication="docs/decisions/drop-acceptance-test-2.md",
        )
        self.assertEqual(accepted["status"], "pass", accepted)
        self.assertTrue(accepted["loosened"])
        self.assertEqual(accepted["adjudication_ref"], "docs/decisions/drop-acceptance-test-2.md")
        document = json.loads((root / ".pipeline" / TASK_ID / "amendments.json").read_text(encoding="utf-8"))
        self.assertEqual(document["revisions"][0]["loosened"], True)
        self.assertEqual(document["revisions"][0]["reason"], "drop an acceptance test")

    def _write_bound_evidence(self, root, head, revision, baseline, *, bind=True):
        """Write a complete evidence set, optionally with the revision binding."""
        directory = root / ".pipeline" / TASK_ID
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "test.log").write_text("observed\n", encoding="utf-8")
        binding = (
            {"sheet_revision": revision, "sheet_sha256": baseline, "observed_at_commit": head}
            if bind else {}
        )
        for name, role in (
            ("executor-report.md", "executor"),
            ("review-report.md", "reviewer"),
            ("final-check.md", "main-final"),
        ):
            report = {
                "schema": 2, "task_id": TASK_ID, "worktree": str(root), "branch": "master",
                "head": head, "generated_at": "2026-01-01T00:00:00+00:00", "role": role, "round": 1,
                "status": "PASS",
                "commands": [{"command": "python -m pytest -q", "exit_code": 0, "evidence_ref": "test.log"}],
                "assertions": ["observed"], "evidence_refs": ["test.log"], "unverified": [],
                **binding,
            }
            (directory / name).write_text(
                "report\n```pipeline-evidence\n" + json.dumps(report) + "\n```\n", encoding="utf-8"
            )
        for name, role in (
            ("executor-result.json", "executor"),
            ("reviewer-result.json", "reviewer"),
            ("final-result.json", "main-final"),
        ):
            (directory / name).write_text(
                json.dumps({
                    "schema": 1, "task_id": TASK_ID, "role": role, "status": "pass", "exit_code": 0,
                    "acceptance": [{"id": "acceptance-test-1", "status": "pass", "exit_code": 0,
                                    "evidence_refs": ["test.log"]}],
                    "unverified": [],
                    **binding,
                }),
                encoding="utf-8",
            )
        return directory

    def test_loosening_covers_the_task_level_evidence_floor(self):
        from pipeline_tools.task_lifecycle import init_task, lifecycle_status

        strict = self._contract(required_evidence_levels=[3])
        strict["acceptance_tests"][0]["evidence_level"] = 3
        root, sheet, _head = self._frozen_repo(contract=strict)
        self.assertEqual(init_task(root, TASK_ID)["evidence"]["required_level"], 3)

        lowered = dict(strict, required_evidence_levels=[2])
        refused = self._amend(root, sheet, lowered, reason="lower the task evidence floor")
        self.assertEqual(refused["status"], "blocked", refused)
        self.assertTrue(any("adjudication" in error for error in refused["errors"]), refused["errors"])
        self.assertFalse((root / ".pipeline" / TASK_ID / "amendments.json").exists())
        self.assertEqual(
            hashlib.sha256(self.last_sheet_text.encode("utf-8")).hexdigest(), digest(sheet)
        )
        write_exact(sheet, self._sheet_text(strict))
        self.assertEqual(lifecycle_status(root, TASK_ID)["evidence"]["required_level"], 3)

        accepted = self._amend(
            root, sheet, lowered, reason="lower the task evidence floor",
            adjudication="docs/decisions/evidence-floor.md",
        )
        self.assertEqual(accepted["status"], "pass", accepted)
        self.assertTrue(accepted["loosened"])
        self.assertTrue(accepted["verification_surface_changed"])
        self.assertEqual(accepted["changes"]["required_evidence_levels"], {"added": [2], "removed": [3]})
        self.assertEqual(accepted["adjudication_ref"], "docs/decisions/evidence-floor.md")
        # The floor the lifecycle reads really did move from 3 down to 2.
        self.assertEqual(lifecycle_status(root, TASK_ID)["evidence"]["required_level"], 2)

    def test_reconcile_reports_the_revision_bound_evidence(self):
        root, sheet, head = self._frozen_repo()
        revision, baseline = task_sheet_revision(root, TASK_ID)
        self._write_bound_evidence(root, head, revision, baseline)
        value = reconcile_task(root, sheet)
        self.assertEqual(value["sheet_revision"], revision)
        self.assertEqual(value["sheet_sha256"], baseline)
        self.assertFalse(value["evidence_validity"]["executor-report.md"]["stale"], value["evidence_validity"])
        self.assertEqual([error for error in value["errors"] if "produced against task sheet revision" in error], [])

    def test_legacy_evidence_without_revision_fields_keeps_its_verdict(self):
        """Evidence in the historical shape must not collect new errors."""
        root, sheet, head = self._frozen_repo()
        revision, baseline = task_sheet_revision(root, TASK_ID)

        legacy_records = {
            "executor-report.md": {"schema": 2, "acceptance": [{"id": "acceptance-test-1"}]},
            "executor-result.json": {"schema": 1, "acceptance": [{"id": "acceptance-test-1"}]},
        }
        status = evidence_revision_status(root, TASK_ID, self._contract(), legacy_records)
        self.assertEqual(status["errors"], [], status)
        self.assertFalse(status["stale"])
        for name, detail in status["records"].items():
            self.assertFalse(detail["revision_bound"], detail)
            self.assertFalse(detail["stale"], detail)
            self.assertEqual(detail["reasons"], [])
            self.assertIsNone(detail["sheet_revision"])
        self.assertEqual(status["unverified"], [
            f"{name} does not record the task sheet revision it was judged against; "
            "the revision criteria were not applied"
            for name in sorted(legacy_records)
        ], status["unverified"])

        # The same evidence set with and without the binding fields must reach the
        # same verdict: a missing new field never changes PASS/BLOCKED on its own.
        self._write_bound_evidence(root, head, revision, baseline, bind=False)
        legacy = reconcile_task(root, sheet)
        self.assertEqual([error for error in legacy["errors"] if "revision" in error], [], legacy["errors"])
        self.assertEqual(
            [error for error in legacy["errors"] if "produced before changes" in error], [], legacy["errors"]
        )
        self._write_bound_evidence(root, head, revision, baseline)
        bound = reconcile_task(root, sheet)
        self.assertEqual(bound["status"], legacy["status"], (bound, legacy))
        self.assertEqual(bound["errors"], legacy["errors"], (bound["errors"], legacy["errors"]))

        # A record that does claim a revision is still judged by the new criteria.
        mismatched = evidence_revision_status(
            root, TASK_ID, self._contract(),
            {"executor-result.json": {
                "schema": 1, "sheet_revision": revision + 1,
                "sheet_sha256": baseline, "observed_at_commit": head,
                "acceptance": [{"id": "acceptance-test-1"}],
            }},
        )
        self.assertTrue(mismatched["stale"], mismatched)
        self.assertTrue(
            any("current revision" in reason for reason in mismatched["errors"]), mismatched["errors"]
        )


    def test_lifecycle_follows_the_recorded_revision(self):
        from pipeline_tools.task_lifecycle import init_task, inspect_task

        root, sheet, _head = self._frozen_repo()
        self.assertEqual(init_task(root, TASK_ID)["state"], "pending")

        # An unrecorded edit is still identity drift for the lifecycle reader.
        write_exact(sheet, self._sheet_text(self._contract(), prose="契约说明：未登记的改动"))
        drifted = inspect_task(root, TASK_ID)
        self.assertEqual(drifted["status"], "blocked", drifted)
        self.assertIn("task sheet hash drift", drifted["errors"])
        write_exact(sheet, self._sheet_text(self._contract()))

        # A recorded amendment moves the baseline and the task keeps going.
        value = self._amend(
            root, sheet, self._contract(), prose="契约说明：登记过的修订", reason="clarify the prose"
        )
        self.assertEqual(value["status"], "pass", value)
        continued = inspect_task(root, TASK_ID)
        self.assertEqual(continued["status"], "pass", continued)
        self.assertEqual(continued["state"], "pending")


if __name__ == "__main__":
    unittest.main()
