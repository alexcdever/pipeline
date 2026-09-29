"""Task-level lifecycle state, identity binding, and evidence gates."""

from __future__ import annotations

import hashlib
import json
import getpass
import os
import tempfile
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .layout import active_pipeline_dir, read_pipeline_dirs
from .contract import validate_task
from .core import evidence_verify

STATES = ("pending", "active", "review", "ready", "merged", "blocked", "abandoned")
TRANSITIONS = {
    "pending": {"active", "blocked", "abandoned"},
    "active": {"review", "blocked", "abandoned"},
    "review": {"ready", "active", "blocked", "abandoned"},
    "ready": {"merged", "active", "blocked", "abandoned"},
    "blocked": {"active", "abandoned"},
    "merged": set(),
    "abandoned": set(),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_task_id(task_id: str) -> str:
    if not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id):
        raise ValueError("invalid task id")
    return task_id


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _task_sheet(root: Path, task_id: str) -> Path:
    return root / "docs" / "tasks" / f"{task_id}.md"


def _identity(root: Path, task_id: str, identity: str | None = None) -> dict[str, str]:
    sheet = _task_sheet(root, task_id)
    return {
        "task_id": task_id,
        "task_sheet": str(sheet),
        "task_sheet_sha256": _sha256(sheet) or "",
        "root": str(root.resolve()),
        "user": identity or getpass.getuser(),
    }


def _directory(root: Path, task_id: str, *, create: bool = False) -> Path:
    if create:
        return active_pipeline_dir(root) / task_id
    for pipeline in read_pipeline_dirs(root):
        candidate = pipeline / task_id
        if candidate.exists():
            return candidate
    return root / ".pipeline" / task_id


def _state_path(root: Path, task_id: str) -> Path:
    return _directory(root, task_id) / "lifecycle.json"


def _read_state(root: Path, task_id: str) -> dict[str, Any] | None:
    path = _state_path(root, task_id)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    recorded = (value.get("identity") or {}).get("task_sheet_sha256")
    observed = _sha256(_task_sheet(root, task_id)) or ""
    if recorded != observed:
        return _result("blocked", task_id, state=value.get("state"), errors=["task sheet hash drift"], observed_task_sheet_sha256=observed, recorded_task_sheet_sha256=recorded)
    return value


def _summary(state: dict[str, Any], root: Path, task_id: str) -> dict[str, Any]:
    current = state.get("state")
    return {
        **state,
        "status": "pass",
        "next_actions": [f"transition:{target}" for target in sorted(TRANSITIONS.get(current, set()))],
        "forbidden_actions": [] if current not in {"merged", "abandoned"} else ["transition", "event"],
        "must_read": [f"docs/tasks/{task_id}.md", ".pipeline/{task-id}/lifecycle.json"],
        "evidence": _evidence(root, task_id),
    }


def _require_writer(role: str) -> list[str]:
    return [] if role == "main-agent" else ["role=main-agent is required for lifecycle writes"]


def _load_contract(root: Path, task_id: str) -> dict[str, Any]:
    sheet = _task_sheet(root, task_id)
    try:
        text = sheet.read_text(encoding="utf-8")
    except OSError:
        return {}
    match = re.search(r"```pipeline-contract\s*\n(.*?)\n```", text, re.DOTALL)
    if not match:
        return {}
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _evidence(root: Path, task_id: str, evidence: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    canonical = root / ".pipeline" / task_id
    directory = evidence or _directory(root, task_id)
    errors: list[str] = []
    try:
        if directory.is_symlink() or directory.resolve() != canonical:
            errors.append("evidence directory must be the canonical .pipeline/<task-id> directory")
        if task_id != canonical.name or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id):
            errors.append("invalid task id")
    except (OSError, RuntimeError):
        errors.append("evidence directory is unreadable")
    contract = _load_contract(root, task_id)
    required = contract.get("required_evidence_levels", [])
    floor = max(required) if isinstance(required, list) and required else 0
    found = 0
    for name in ("executor-result.json", "reviewer-result.json", "final-result.json", "executor-report.md", "review-report.md", "final-check.md"):
        if (directory / name).is_file():
            found = max(found, 2 if name.endswith("result.json") else 1)
    return {"directory": str(directory), "required_level": floor, "observed_level": found, "ready": found >= floor and not errors, "errors": errors, "task_sheet_sha256": _sha256(_task_sheet(root, task_id))}


def _result(status: str, task_id: str, **extra: Any) -> dict[str, Any]:
    return {"schema": 1, "command": "lifecycle", "status": status, "task_id": task_id, **extra}


def _atomic_write_state(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _write_event(directory: Path, event: dict[str, Any]) -> None:
    with (directory / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True) + "\n")


def init_task(root: Path, task_id: str, identity: str | None = None, *, create: bool = True) -> dict[str, Any]:
    task_id = _safe_task_id(task_id)
    root = root.resolve()
    directory = _directory(root, task_id, create=create)
    existing = _read_state(root, task_id)
    bound = _identity(root, task_id, identity)
    if existing:
        if existing.get("status") == "blocked":
            return existing
        if existing.get("identity") != bound:
            return _result("blocked", task_id, errors=["task identity drift"], identity=existing.get("identity"), observed=bound)
        return existing
    if not create:
        return _result("blocked", task_id, errors=["lifecycle state is not initialized"], next_actions=["resume with role=main-agent"])
    directory.mkdir(parents=True, exist_ok=True)
    state = {"schema": 1, "task_id": task_id, "state": "pending", "identity": bound, "created_at": _now(), "updated_at": _now(), "evidence": _evidence(root, task_id)}
    _atomic_write_state(directory / "lifecycle.json", state)
    _write_event(directory, {"type": "created", "at": _now(), "identity": bound})
    return _summary(state, root, task_id)


def list_tasks(root: Path) -> dict[str, Any]:
    items = []
    for directory in read_pipeline_dirs(root):
        if directory.is_dir():
            for path in sorted(directory.glob("*/lifecycle.json")):
                value = _read_state(root, path.parent.name)
                if value and value.get("status") != "blocked":
                    items.append({"task_id": value.get("task_id"), "state": value.get("state"), "updated_at": value.get("updated_at")})
    return _result("pass", "*", tasks=items, next_actions=["inspect a task"], forbidden_actions=["write lifecycle state"], must_read=[".pipeline/<task-id>/lifecycle.json"], evidence={"task_count": len(items)})


def inspect_task(root: Path, task_id: str) -> dict[str, Any]:
    state = init_task(root, task_id, create=False)
    if state.get("status") == "blocked":
        return state
    return _summary(state, root, task_id)


def resume_task(root: Path, task_id: str, identity: str | None = None) -> dict[str, Any]:
    state = init_task(root, task_id, identity, create=False)
    if state.get("status") == "blocked":
        return state
    allowed = sorted(TRANSITIONS.get(state.get("state"), set()))
    return _result("pass", task_id, state=state.get("state"), recovery_summary={"current_state": state.get("state"), "can_resume": bool(allowed), "allowed_transitions": allowed}, next_actions=[f"transition:{target}" for target in allowed], forbidden_actions=["implicit state transition"], must_read=[f"docs/tasks/{task_id}.md", ".pipeline/<task-id>/lifecycle.json"], evidence=_evidence(root, task_id))


def transition_task(root: Path, task_id: str, target: str, identity: str | None = None, evidence: Path | None = None, *, role: str = "legacy") -> dict[str, Any]:
    task_id = _safe_task_id(task_id)
    if _require_writer(role):
        return _result("blocked", task_id, errors=_require_writer(role), forbidden_actions=["transition"], next_actions=["retry with role=main-agent"])
    if target not in STATES:
        return _result("blocked", task_id, errors=[f"unknown lifecycle state: {target}"])
    sheet = _task_sheet(root, task_id)
    validation_errors = validate_task(sheet)
    if not sheet.is_file() or validation_errors:
        return _result("blocked", task_id, errors=["task sheet must be valid before lifecycle transition", *validation_errors])
    try:
        import subprocess
        relative = sheet.relative_to(root).as_posix()
        head_check = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"HEAD:{relative}"], capture_output=True, check=False)
        status_check = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", relative], capture_output=True, text=True, check=False)
        if head_check.returncode != 0 or status_check.stdout.strip():
            return _result("blocked", task_id, errors=["task sheet must be committed at HEAD with no uncommitted changes"])
    except OSError:
        return _result("blocked", task_id, errors=["unable to verify frozen task sheet"])
    state = init_task(root, task_id, identity, create=True)
    if state.get("status") == "blocked":
        return state
    current = state["state"]
    if current in {"merged", "abandoned"}:
        return _result("blocked", task_id, state=current, errors=[f"terminal state {current} is immutable"])
    if target != current and target not in TRANSITIONS.get(current, set()):
        return _result("blocked", task_id, state=current, errors=[f"illegal transition: {current} -> {target}"], allowed_transitions=sorted(TRANSITIONS.get(current, set())))
    evidence_value = _evidence(root, task_id, evidence)
    if target in {"ready", "merged"}:
        evidence_errors = evidence_verify(Path(evidence_value["directory"]), task_id)
        if evidence_errors or not evidence_value["ready"]:
            return _result("blocked", task_id, state=current, errors=["structured evidence verification failed", *evidence_errors], evidence=evidence_value)
    directory = _directory(root, task_id)
    state.update({"state": target, "updated_at": _now(), "evidence": evidence_value, "status": "pass"})
    _atomic_write_state(directory / "lifecycle.json", state)
    _write_event(directory, {"type": "transition", "from": current, "to": target, "at": _now(), "identity": state["identity"]})
    return state


def append_event(root: Path, task_id: str, event_type: str, data: dict[str, Any] | None = None, identity: str | None = None, *, role: str = "legacy") -> dict[str, Any]:
    if _require_writer(role):
        return _result("blocked", task_id, errors=_require_writer(role), forbidden_actions=["event"], next_actions=["retry with role=main-agent"])
    state = init_task(root, task_id, identity, create=True)
    if state.get("state") in {"merged", "abandoned"}:
        return _result("blocked", task_id, state=state.get("state"), errors=[f"terminal state {state.get('state')} is immutable"])

    if state.get("status") == "blocked":
        return state
    event = {"type": event_type, "at": _now(), "identity": state["identity"], "data": data or {}}
    _write_event(_directory(root, task_id), event)
    return _result("pass", task_id, event=event)


def lifecycle_status(root: Path, task_id: str, evidence_directory: Path | None = None) -> dict[str, Any]:
    state = inspect_task(root, task_id)
    if evidence_directory is not None and state.get("status") != "blocked":
        state["evidence"] = _evidence(root, task_id, evidence_directory)
    return state


__all__ = ["append_event", "init_task", "inspect_task", "lifecycle_status", "list_tasks", "resume_task", "transition_task"]
