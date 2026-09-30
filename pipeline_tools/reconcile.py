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
    evidence_verify,
    normalize_status,
    verify_structured_result,
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
        "branch": {value.get("branch") for value in reports.values()},
        "worktree": {value.get("worktree") for value in reports.values()},
        "head": {value.get("head") for value in reports.values() if value.get("head") is not None},
    }
    identity = {
        "task_id": task_id if identity_values["task_id"] == {task_id} else None,
        "branch": next(iter(identity_values["branch"])) if len(identity_values["branch"]) == 1 else None,
        "worktree": next(iter(identity_values["worktree"])) if len(identity_values["worktree"]) == 1 else None,
        "head": next(iter(identity_values["head"])) if len(identity_values["head"]) == 1 else None,
    }
    identity_errors = []
    if any(len(values) > 1 for values in identity_values.values()):
        identity_errors.append("report identity conflict")
    if reports and any(not value.get(key) for value in reports.values() for key in ("task_id", "branch", "worktree")):
        identity_errors.append("report identity is incomplete")
    try:
        verify_errors = evidence_verify(evidence, str(task_id), identity.get("branch"))
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
    statuses = [value.get("status") for value in reports.values()]
    direct_pass = (not contract_errors and not report_errors and not result_errors and not identity_errors and not verify_errors
                   and readiness["status"] == "ready" and freshness["status"] == "pass"
                   and len(reports) == len(_REPORTS)
                   and all(normalize_status(status, POST_MERGE_REPORT_STATUSES) is not None for status in statuses))
    status = "PASS" if direct_pass else ("BLOCKED" if identity_errors or result_errors or verify_errors or freshness["status"] == "blocked" else "UNVERIFIED")
    if layout_error:
        status = "BLOCKED"
    output = {"schema": 1, "command": "evidence.reconcile", "task_id": task_id, "status": status,
              "identity": identity, "result": {name: value.get("status") for name, value in results.items()},
              "freshness": freshness["status"], "readiness": readiness["status"],
              "verify": "PASS" if not verify_errors else "BLOCKED",
              "observed": {"task_sheet": task_sheet.relative_to(root).as_posix(), "evidence_dir": evidence.relative_to(root).as_posix(), "reports": sorted(reports)},
              "errors": contract_errors + report_errors + result_errors + identity_errors + verify_errors + ([f"布局冲突：{layout_error}"] if layout_error else []),
              "unverified": [] if direct_pass else ["task completion"], "updated": False}
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
    return {"schema": 1, "command": "evidence.reconcile", "status": "pass" if all(item["status"] == "PASS" for item in tasks) else "blocked", "tasks": tasks, "updated": False, "exit_code": 0 if all(item["status"] == "PASS" for item in tasks) else 3}
