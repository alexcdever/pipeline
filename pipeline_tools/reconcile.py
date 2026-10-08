"""Mechanical reconciliation of task sheets and directly readable evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .contract import load_contract
from .core import (
    POST_MERGE_REPORT_STATUSES,
    evidence_freshness,
    evidence_readiness,
    evidence_revision_status,
    evidence_verify,
    git,
    normalize_status,
    verify_structured_result,
    verify_finalization_snapshot,
)
from .layout import LegacyPipelineLayoutError, active_pipeline_dir

_REPORTS = ("executor-report.md", "review-report.md", "final-check.md")
_RESULTS = ("executor-result.json", "reviewer-result.json", "final-result.json")


def _machine_block(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None, ["unreadable"]
    starts = [i for i, line in enumerate(lines) if line.strip() == "```pipeline-evidence"]
    if len(starts) != 1:
        return None, ["missing or duplicate pipeline-evidence block"]
    end = next((i for i in range(starts[0] + 1, len(lines)) if lines[i].strip() == "```"), None)
    if end is None:
        return None, ["pipeline-evidence block is not closed"]
    try:
        value = json.loads("\n".join(lines[starts[0] + 1 : end]))
    except json.JSONDecodeError:
        return None, ["pipeline-evidence JSON is invalid"]
    return (value, []) if isinstance(value, dict) else (None, ["pipeline-evidence must be an object"])


def _json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _report_revision(value: dict[str, Any]) -> int | None:
    """Return a report's declared task sheet revision, or None when it has none."""
    declared = value.get("sheet_revision")
    return declared if isinstance(declared, int) and not isinstance(declared, bool) else None


def _safe_cwd_is_root(value: Any, root: Path) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        candidate = Path(value.strip())
        if not candidate.is_absolute():
            candidate = root / candidate
        return candidate.resolve() == root.resolve()
    except (OSError, TypeError, ValueError, RuntimeError):
        return False


def _delivery_is_merged(root: Path, task_id: str, evidence: Path, branches: set[Any]) -> bool:
    """Return whether a delivery is already merged, so reconcile judges post-merge.

    Two mechanical signals are accepted, and either one is sufficient:

    - the task carries a ``finalized`` marker, which the post-merge sequence only
      writes at its end; and
    - a branch named by the reports -- other than the branch ``HEAD`` is currently
      on -- resolves to a ref whose tip is already an ancestor of ``HEAD``.

    The current branch is never a merge signal: the main-worktree final check
    records the branch it ran on, and that branch's tip is trivially an ancestor
    of ``HEAD`` whether or not the task branch was ever merged.  Left in, it would
    report a plain unmerged task as merged and drop the active commit binding.
    Excluding it leaves only the task's own branch, so an unmerged task keeps a
    branch tip strictly ahead of ``HEAD`` and is still judged active.

    The two signals cannot contradict each other: each is a positive proof of a
    merge, while a branch ref that is missing (deleted after the merge), not an
    ancestor, or equal to the current branch is only absence of the second proof,
    never a claim that the delivery is unmerged.
    """
    marker = _json(evidence / "finalization.json")
    if isinstance(marker, dict) and marker.get("task_id") == task_id and marker.get("status") == "finalized":
        return True
    current_branch = git(root, "branch", "--show-current", redact_output=False)[1].strip()
    for branch in sorted(item for item in branches if isinstance(item, str) and item.strip()):
        if branch == current_branch:
            continue
        if git(root, "rev-parse", "--verify", f"refs/heads/{branch}")[0]:
            continue
        if git(root, "merge-base", "--is-ancestor", branch, "HEAD")[0] == 0:
            return True
    return False


def reconcile_task(root: Path, task_sheet: Path, *, update: bool = False) -> dict[str, Any]:
    root, task_sheet = Path(root).resolve(), Path(task_sheet).resolve()
    contract, contract_errors = load_contract(task_sheet)
    task_id = contract.get("task_id") if contract else task_sheet.stem
    try:
        evidence = active_pipeline_dir(root) / str(task_id)
        layout_error = None
    except (LegacyPipelineLayoutError, OSError) as error:
        evidence = root / ".pipeline" / str(task_id)
        layout_error = str(error)
    reports: dict[str, dict[str, Any]] = {}
    report_errors: list[str] = []
    for name in _REPORTS:
        path = evidence / name
        if not path.is_file():
            report_errors.append(f"missing {name}")
            continue
        value, errors = _machine_block(path)
        if errors or value is None:
            report_errors.extend(f"{name}: {error}" for error in errors)
        else:
            reports[name] = value
    result_roles = {
        "executor-result.json": "executor",
        "reviewer-result.json": "reviewer",
        "final-result.json": "final",
    }
    results = {name: value for name in _RESULTS if (value := _json(evidence / name)) is not None}
    expected_acceptance_ids = {
        item.get("id") for item in (contract or {}).get("acceptance_tests", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    result_errors: list[str] = []
    for name in _RESULTS:
        path = evidence / name
        if not path.is_file():
            result_errors.append(f"missing {name}")
            continue
        result_errors.extend(
            f"{name}: {error}"
            for error in verify_structured_result(
                path, str(task_id), result_roles[name], evidence,
                strict=True, expected_acceptance_ids=expected_acceptance_ids,
            )
        )
    identity_values = {
        "task_id": {value.get("task_id") for value in reports.values()},
        "sheet_revision": {_report_revision(value) for value in reports.values()},
        "branch": {value.get("branch") for value in reports.values()},
        "worktree": {value.get("worktree") for value in reports.values()},
        "head": {value.get("head") for value in reports.values() if value.get("head") is not None},
    }
    identity = {
        "task_id": task_id if identity_values["task_id"] == {task_id} else None,
        "sheet_revision": next(iter(identity_values["sheet_revision"])) if len(identity_values["sheet_revision"]) == 1 else None,
        "branch": next(iter(identity_values["branch"])) if len(identity_values["branch"]) == 1 else None,
        "worktree": next(iter(identity_values["worktree"])) if len(identity_values["worktree"]) == 1 else None,
        "head": next(iter(identity_values["head"])) if len(identity_values["head"]) == 1 else None,
    }
    identity_errors = []
    # Identity is the task id plus the task sheet revision.  branch, worktree and
    # head stay recorded facts: a task-branch report and the main-worktree final
    # check legitimately disagree on them, so they never make an identity conflict.
    # A report that declares no revision keeps the historical shape's verdict --
    # evidence_revision_status reports it as unverified, never as a new error.
    if len(identity_values["task_id"]) > 1 or len(identity_values["sheet_revision"]) > 1:
        identity_errors.append("report identity conflict")
    if reports and any(not value.get("task_id") for value in reports.values()):
        identity_errors.append("report identity is incomplete")
    heads = identity_values["head"]
    strict_reports = [value for value in reports.values() if value.get("schema") == 2]
    if heads and any(not isinstance(head, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", head) for head in heads):
        identity_errors.append("report HEAD is not a valid commit")
    if strict_reports and len(strict_reports) != len(reports):
        identity_errors.append("report schema versions are inconsistent")
    if strict_reports and not heads:
        identity_errors.append("new-schema reports must declare HEAD")
    if reports and len(strict_reports) != len(_REPORTS):
        identity_errors.append("schema 1 reports are legacy/unverified and cannot support final PASS")
    try:
        # The phase selects the identity criterion set.  A merged delivery is
        # identified by the task id plus the sheet revision: merging always moves
        # HEAD past the commits the reports recorded, so the active commit binding
        # could never hold there.  An unmerged task keeps that binding.
        phase = "finalized" if _delivery_is_merged(
            root, str(task_id), evidence, identity_values["branch"]
        ) else "active"
        verify_errors = evidence_verify(evidence, str(task_id), identity.get("branch"), phase)
        readiness = evidence_readiness(evidence, str(task_id))
    except (LegacyPipelineLayoutError, OSError) as error:
        verify_errors = [f"布局冲突：{error}"]
        readiness = {"status": "not_ready"}
    result_path = evidence / "final-result.json"
    if not result_path.is_file():
        result_path = evidence / "reviewer-result.json"
    try:
        freshness = evidence_freshness(root, evidence, result_path if result_path.is_file() else None)
    except (LegacyPipelineLayoutError, OSError) as error:
        freshness = {"status": "blocked", "errors": [f"布局冲突：{error}"]}
    bound_records = {**reports, **results}
    try:
        # Reconciliation is the post-merge judgment: merging always moves HEAD past
        # the recorded observation commit, so the changed-path criterion is not
        # judged here; identity is the task id plus the sheet revision.
        revision_status = evidence_revision_status(
            root, str(task_id), contract or {}, bound_records, judge_observed_paths=False
        )
    except (LegacyPipelineLayoutError, OSError) as error:
        revision_status = {"schema": 1, "sheet_revision": None, "sheet_sha256": None, "head": None,
                           "records": {}, "stale": True, "errors": [f"布局冲突：{error}"], "unverified": []}
    revision_errors = revision_status["errors"]
    revision_unverified = revision_status.get("unverified", [])
    statuses = [value.get("status") for value in reports.values()]
    finalization_errors: list[str] = []
    finalization = _json(evidence / "finalization.json")
    if finalization is None:
        finalization_errors.append("missing or invalid finalization.json")
    elif finalization.get("task_id") != task_id or finalization.get("status") != "finalized":
        finalization_errors.append("finalization identity or status is invalid")
    else:
        finalization_errors.extend(verify_finalization_snapshot(evidence, finalization, root))
    post_merge_errors = []
    if not reports:
        post_merge_errors.append("no reports available")
    elif reports.get("final-check.md", {}).get("role") != "main-final":
        post_merge_errors.append("final-check is required for post-merge finalization")
    if not any(
        isinstance(command, dict)
        and command.get("exit_code") == 0
        and isinstance(command.get("cwd"), str)
        and command.get("cwd").strip()
        and _safe_cwd_is_root(command.get("cwd"), root)
        for command in reports.get("final-check.md", {}).get("commands", [])
    ):
        post_merge_errors.append("main worktree post-merge re-verification is missing")
    if any(normalize_status(status, ("BLOCKED",)) == "BLOCKED" for status in statuses):
        post_merge_errors.append("report declares BLOCKED")
    direct_pass = (not contract_errors and not report_errors and not result_errors and not identity_errors and not verify_errors
                   and not finalization_errors and not post_merge_errors and not revision_errors
                   and readiness["status"] == "ready" and freshness["status"] == "pass"
                   and len(reports) == len(_REPORTS)
                   and all(normalize_status(status, POST_MERGE_REPORT_STATUSES) is not None for status in statuses))
    status = "PASS" if direct_pass else ("BLOCKED" if identity_errors or result_errors or verify_errors or finalization_errors or post_merge_errors or revision_errors or freshness["status"] == "blocked" else "UNVERIFIED")
    if layout_error:
        status = "BLOCKED"
    output = {"schema": 1, "command": "evidence.reconcile", "task_id": task_id, "status": status,
              "identity": identity, "result": {name: value.get("status") for name, value in results.items()},
              "freshness": freshness["status"], "readiness": readiness["status"],
              "sheet_revision": revision_status["sheet_revision"], "sheet_sha256": revision_status["sheet_sha256"],
              "evidence_validity": revision_status["records"],
              "verify": "PASS" if not verify_errors else "BLOCKED",
              "observed": {"task_sheet": task_sheet.relative_to(root).as_posix(), "evidence_dir": evidence.relative_to(root).as_posix(), "reports": sorted(reports)},
              "errors": contract_errors + report_errors + result_errors + identity_errors + verify_errors + finalization_errors + post_merge_errors + revision_errors + ([f"布局冲突：{layout_error}"] if layout_error else []),
              "unverified": ([] if direct_pass else ["task completion"]) + revision_unverified, "updated": False}
    if update:
        output["errors"].append("--update is deprecated and cannot modify task sheets")
        output["status"] = "BLOCKED"
        output["updated"] = False
    return output


def reconcile_tasks(root: Path, task_id: str | None = None, *, update: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    sheets = sorted((root / "docs" / "tasks").glob("*.md"))
    selected = [sheet for sheet in sheets if task_id is None or sheet.stem == task_id]
    tasks = [reconcile_task(root, sheet, update=update) for sheet in selected]
    complete = bool(tasks) and all(item["status"] == "PASS" for item in tasks)
    return {"schema": 1, "command": "evidence.reconcile", "status": "pass" if complete else "blocked", "tasks": tasks, "updated": False, "exit_code": 0 if complete else 3}
