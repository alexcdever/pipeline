"""Mechanical planning facts, progress, and evidence lifecycle checks.

This module deliberately validates structure and filesystem/process facts only.  It
never tries to decide whether a requirement is a good product decision.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .contract import (
    DEFAULT_PROJECT_TYPE,
    PROJECT_TYPES,
    RISK_LEVELS,
    evidence_floor,
    load_contract,
    validate_task,
)
from .core import RETAINED_EVIDENCE_NAMES
from .layout import (
    LEGACY_PIPELINE_DIR_NAME,
    PIPELINE_DIR_NAME,
    LegacyPipelineLayoutError,
    active_pipeline_dir,
    migrate_layout,
)

CHAIN = ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")
ROLES = {"executor", "reviewer", "main"}
TASK_TYPES = {"vertical-feature", "prerequisite", "repair", "derived"}
GOAL_DOCUMENT_NAME = "goal.md"
LEGACY_PLAN_DOCUMENT_NAME = "implement-plan.md"
IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
ACCEPTANCE_ID_RE = re.compile(r"acceptance-test-[A-Za-z0-9][A-Za-z0-9._-]*\Z")
WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")
SENSITIVE_NAME_RE = re.compile(
    r"(?i)(?:password|passwd|secret|token|api[_-]?key|authorization|bearer|cvc)"
)
SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)(?:password|passwd|secret|token|api[_-]?key|authorization|cvc)"
    r"\s*(?:=|:)\s*['\"]?[^\s,'\"}]+"
)
BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{6,}")
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME)\b|<\s*(?:placeholder|fill[-_ ]?in|your[-_ ]?value|\.\.\.)\s*>", re.IGNORECASE)
CONCEPTUAL_PLAN_TOKENS = {"task-id", "planning-run-id"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_goal_document(root: Path) -> tuple[Path, str | None]:
    """Resolve the authoritative requirements document.

    ``goal.md`` is authoritative. When only the legacy ``implement-plan.md``
    exists it is mechanically copied into ``goal.md`` with a source header, so
    the conversion is a byte-faithful move rather than a semantic rewrite. When
    neither file exists the caller must ask a human to create ``goal.md``.
    """
    root = Path(root)
    goal = root / GOAL_DOCUMENT_NAME
    legacy = root / LEGACY_PLAN_DOCUMENT_NAME
    if goal.is_file():
        return goal, None
    if not legacy.is_file():
        return goal, f"{GOAL_DOCUMENT_NAME} missing and no {LEGACY_PLAN_DOCUMENT_NAME} to convert"
    try:
        content = legacy.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return goal, f"{LEGACY_PLAN_DOCUMENT_NAME} is unreadable"
    header = (
        f"<!-- Generated from {LEGACY_PLAN_DOCUMENT_NAME} by pipeline_tools goal-sync. "
        f"{GOAL_DOCUMENT_NAME} is the authoritative requirements document; edit it directly from now on. -->\n"
    )
    try:
        goal.write_text(header + content, encoding="utf-8")
    except OSError:
        return goal, f"unable to write {GOAL_DOCUMENT_NAME}"
    return goal, None


def _normalise_text(value: Any) -> str:
    return str(value).replace("\\", "/") if value is not None else ""


def _safe_rel(root: Path, value: str) -> bool:
    """Return whether *value* is a safe project-relative path.

    The lexical check catches traversal even when the target does not exist.  The
    resolved check also rejects a symlink which points outside the project.
    """
    text = _normalise_text(value)
    if not text.strip() or "\x00" in text:
        return False
    if text.startswith("/") or WINDOWS_ABSOLUTE_RE.match(text):
        return False
    parts = PurePosixPath(text).parts
    if not parts or any(part in {"..", ""} for part in parts):
        return False
    try:
        root_resolved = root.resolve()
        candidate = (root / Path(*parts)).resolve()
        return candidate == root_resolved or candidate.is_relative_to(root_resolved)
    except (OSError, RuntimeError, ValueError):
        return False


def _safe_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(IDENTIFIER_RE.fullmatch(value))


def _safe_entity_identifier(value: Any) -> bool:
    """Allow path-like compatibility identifiers but never traversal."""
    return (
        isinstance(value, str)
        and bool(value.strip())
        and "\\x00" not in value
        and not value.startswith(("/", "\\"))
        and ".." not in PurePosixPath(value.replace("\\\\", "/")).parts
        and not PLACEHOLDER_RE.search(value)
    )


def _safe_task_id(value: Any) -> bool:
    return _safe_identifier(value)


def _safe_reference(value: Any) -> bool:
    """Validate a relative reference without requiring a project root."""
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        return False
    text = value.replace("\\", "/")
    return not (
        text.startswith("/")
        or WINDOWS_ABSOLUTE_RE.match(text)
        or any(part in {"..", ""} for part in PurePosixPath(text).parts)
        or PLACEHOLDER_RE.search(text) is not None
    )


def _run_checked(command: list[str], cwd: Path, timeout: float = 10) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", "executable unavailable"
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"
    return result.returncode, result.stdout or "", result.stderr or ""


def _parse_worktrees(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line == "worktree" or line.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"path": line[len("worktree"):].strip()}
        elif current is not None and line.startswith("HEAD "):
            current["head"] = line[5:].strip()
        elif current is not None and line.startswith("branch "):
            current["branch"] = line[7:].strip()
        elif current is not None and line == "detached":
            current["branch"] = "(detached)"
    if current:
        entries.append(current)
    return entries


def _worktree_facts(root: Path) -> tuple[dict[str, Any], list[str]]:
    facts: dict[str, Any] = {"root": str(root.resolve()), "registered": False}
    errors: list[str] = []
    rc, top, err = _run_checked(["git", "-C", str(root), "rev-parse", "--show-toplevel"], root)
    if rc:
        errors.append("Git repository unavailable")
        facts["error"] = err.strip() or top.strip()
        return facts, errors
    try:
        actual_root = Path(top.strip()).resolve()
        facts["git_root"] = str(actual_root)
    except (OSError, ValueError):
        errors.append("Git worktree root is unreadable")
        return facts, errors
    if actual_root != root.resolve():
        errors.append("planning root is not the Git worktree root")

    rc, head, err = _run_checked(["git", "-C", str(root), "rev-parse", "HEAD"], root)
    if rc:
        errors.append("Git HEAD unavailable")
    else:
        facts["head"] = head.strip()
    rc, branch, err = _run_checked(["git", "-C", str(root), "branch", "--show-current"], root)
    if rc:
        errors.append("Git branch unavailable")
    else:
        facts["branch"] = branch.strip() or "(detached)"
    rc, listing, err = _run_checked(["git", "-C", str(root), "worktree", "list", "--porcelain"], root)
    if rc:
        errors.append("Git worktree list unavailable")
        return facts, errors
    entries = _parse_worktrees(listing)
    facts["worktrees"] = entries
    matching: list[dict[str, str]] = []
    for entry in entries:
        try:
            if Path(entry.get("path", "")).resolve() == root.resolve():
                matching.append(entry)
        except (OSError, ValueError):
            continue
    if len(matching) != 1:
        errors.append("worktree is not registered exactly once")
    else:
        facts["registered"] = True
        facts["worktree"] = matching[0]
    # A checkout which resolves to the repository root but is not listed by
    # `git worktree list` is an orphan, even if a copied .git file happens to
    # make Git commands work.  This is decided from Git facts, not from a path
    # fragment, so a project that merely lives in a directory named
    # `.worktrees` is not misreported.
    if actual_root == root.resolve() and not facts["registered"]:
        errors.append("isolated worktree is orphaned")
    common_rc, common, _ = _run_checked(["git", "-C", str(root), "rev-parse", "--git-common-dir"], root)
    if common_rc == 0:
        try:
            common_path = Path(common.strip())
            if not common_path.is_absolute():
                common_path = (root / common_path).resolve()
            facts["common_git_dir"] = str(common_path)
            facts["isolated_worktree"] = common_path.parent.resolve() != root.resolve()
        except (OSError, ValueError):
            facts["isolated_worktree"] = False
    return facts, errors


def _write_preflight_failure(root: Path, value: dict[str, Any]) -> list[str]:
    """Persist a diagnostic only when doing so cannot overwrite a conflict."""
    workflow = root / ".workflow"
    pipeline = root / ".pipeline"
    if workflow.exists() and pipeline.exists():
        return []
    try:
        if pipeline.is_symlink():
            return []
        active_pipeline_dir(root)
        output = pipeline / "planning" / "preflight-result.json"
        if not _safe_rel(root, output.relative_to(root).as_posix()):
            return []
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(".tmp")
        temporary.write_text(json.dumps(value, ensure_ascii=True, indent=2), encoding="utf-8")
        os.replace(temporary, output)
        return [str(output)]
    except (OSError, ValueError, RuntimeError):
        return []


def _clear_stale_preflight_failure(root: Path) -> None:
    """Drop the diagnostic left by an earlier failed preflight.

    A preflight without a run id files its failure at
    ``.pipeline/planning/preflight-result.json``.  Nothing removed it, so a
    single failure kept ``.pipeline/planning/`` alive forever.  A later
    successful check clears it, which makes the record mean "the last
    preflight failed" instead of "a preflight failed once".
    """
    try:
        output = root / PIPELINE_DIR_NAME / "planning" / "preflight-result.json"
        if output.is_file():
            output.unlink()
        directory = output.parent
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    except OSError:
        return


def _sheet_committed(root: Path, task_id: str) -> bool:
    """Return whether docs/tasks/<task_id>.md exists in the current HEAD commit."""
    relative = f"docs/tasks/{task_id}.md"
    rc, _output, _error = _run_checked(["git", "cat-file", "-e", f"HEAD:{relative}"], root)
    return rc == 0


def _task_scene_facts(root: Path) -> tuple[list[str], list[str], dict[str, list[str]]]:
    """Report pre-existing task scenes without judging their product meaning.

    A task worktree without a frozen task sheet violates the recorded invariant
    that no task worktree may exist without its committed sheet, and a sheet
    that is present on disk but absent from HEAD is not frozen either; a sheet
    without a worktree and leftover task evidence are reported as warnings so an
    interrupted earlier run is visible before a new one starts.
    """
    warnings: list[str] = []
    errors: list[str] = []
    scenes: dict[str, list[str]] = {
        "sheets_without_worktree": [],
        "worktrees_without_sheet": [],
        "uncommitted_sheets": [],
        "leftover_evidence": [],
    }
    sheets: dict[str, Path] = {}
    tasks_directory = root / "docs" / "tasks"
    try:
        if tasks_directory.is_dir():
            for path in sorted(tasks_directory.glob("*.md")):
                if path.is_file():
                    sheets[path.stem] = path
    except OSError:
        warnings.append("task sheet directory is unreadable")
    worktrees: dict[str, Path] = {}
    worktree_directory = root / ".worktrees"
    try:
        if worktree_directory.is_dir():
            for path in sorted(worktree_directory.iterdir()):
                if path.is_dir() and not path.is_symlink():
                    worktrees[path.name] = path
    except OSError:
        warnings.append(".worktrees directory is unreadable")
    evidence: dict[str, Path] = {}
    try:
        pipeline_directory = active_pipeline_dir(root)
    except (LegacyPipelineLayoutError, OSError):
        pipeline_directory = root / PIPELINE_DIR_NAME
    try:
        if pipeline_directory.is_dir():
            for path in sorted(pipeline_directory.iterdir()):
                if path.is_dir() and path.name not in {"planning", "metrics"}:
                    evidence[path.name] = path
    except OSError:
        warnings.append(".pipeline directory is unreadable")

    for task_id in sorted(set(sheets) - set(worktrees)):
        scenes["sheets_without_worktree"].append(task_id)
    for task_id in sorted(set(worktrees) - set(sheets)):
        scenes["worktrees_without_sheet"].append(task_id)
        errors.append(f"task worktree has no committed task sheet: {task_id}")
    for task_id in sorted(set(worktrees) & set(sheets)):
        if not _sheet_committed(root, task_id):
            scenes["uncommitted_sheets"].append(task_id)
            errors.append(f"task sheet is not committed in HEAD: {task_id}")
    for task_id in sorted(set(evidence) - set(sheets)):
        scenes["leftover_evidence"].append(task_id)
    if scenes["sheets_without_worktree"]:
        warnings.append(
            "task sheets without worktrees: " + ", ".join(scenes["sheets_without_worktree"])
        )
    if scenes["leftover_evidence"]:
        warnings.append(
            "leftover task evidence directories: " + ", ".join(scenes["leftover_evidence"])
        )
    return warnings, errors, scenes


def planning_preflight(
    root: Path,
    tool_available: bool = True,
    *,
    expected_requirements_sha256: str | None = None,
    expected_head: str | None = None,
    expected_branch: str | None = None,
    expected_worktree: Path | None = None,
) -> dict[str, Any]:
    """Run fail-closed checks before any planning or worktree dispatch.

    The optional identity/hash arguments are used by later lifecycle phases to
    detect drift; the ordinary planning call still verifies the live identity.
    """
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[dict[str, str]] = []
    plan = root / GOAL_DOCUMENT_NAME
    requirements_hash: str | None = None
    if not root.is_dir():
        errors.append("project root is unavailable")
    legacy = root / LEGACY_PIPELINE_DIR_NAME
    pipeline = root / PIPELINE_DIR_NAME
    if legacy.exists() and pipeline.exists():
        errors.append(".workflow and .pipeline both exist")
    elif legacy.exists():
        # A lone legacy tree is migrated in place; only the canonical path is
        # used for every later planning decision.
        try:
            migrate_layout(root)
        except (LegacyPipelineLayoutError, OSError) as error:
            errors.append(f"legacy .workflow migration failed: {error}")
        else:
            warnings.append("legacy .workflow migrated to .pipeline")

    if root.is_dir():
        plan, sync_error = sync_goal_document(root)
        if sync_error:
            errors.append(sync_error)
        else:
            try:
                content = plan.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                content = ""
                errors.append(f"{GOAL_DOCUMENT_NAME} is unreadable")
            if not content.strip():
                errors.append(f"{GOAL_DOCUMENT_NAME} is empty")
            elif PLACEHOLDER_RE.search(content):
                errors.append(f"{GOAL_DOCUMENT_NAME} contains placeholders")
            else:
                requirements_hash = _sha256(plan)

    if not tool_available:
        errors.append("pipeline tool unavailable")
    elif importlib.util.find_spec("pipeline_tools") is None:
        errors.append("pipeline tool package unavailable")
    else:
        # Check the actual executable used to run the tool, without enabling
        # automatic metrics or writing anything in the project.  Run from the
        # checkout that owns this module, not from the caller's project root:
        # a planning target may be a temporary project without this package.
        env = dict(os.environ)
        env["PIPELINE_TOOLS_DISABLE_AUTO_METRICS"] = "1"
        try:
            tool_root = Path(__file__).resolve().parent.parent
            command = [sys.executable, "-m", "pipeline_tools", "--help"]
            tool_env = dict(env)
            existing_pythonpath = tool_env.get("PYTHONPATH", "")
            tool_env["PYTHONPATH"] = str(tool_root) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
            result = subprocess.run(
                command,
                cwd=tool_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                env=tool_env,
                check=False,
            )
            if result.returncode != 0:
                errors.append("pipeline tool command failed")
        except (OSError, subprocess.SubprocessError):
            errors.append("pipeline tool command unavailable")

    git_available = shutil.which("git") is not None
    python_available = shutil.which("python") is not None or bool(sys.executable)
    if not git_available:
        errors.append("required command unavailable: git")
    if not python_available:
        errors.append("required command unavailable: python")
    if git_available and root.is_dir():
        _git_rc, _git_out, _git_err = _run_checked(["git", "--version"], root)
        if _git_rc:
            errors.append("required command unavailable: git")
    if python_available:
        try:
            version = subprocess.run(
                [sys.executable, "--version"], capture_output=True, text=True, timeout=10, check=False
            )
            if version.returncode != 0:
                errors.append("required command unavailable: python")
        except (OSError, subprocess.SubprocessError):
            errors.append("required command unavailable: python")

    worktree: dict[str, Any] = {}
    if root.is_dir() and git_available:
        worktree, identity_errors = _worktree_facts(root)
        errors.extend(identity_errors)
    else:
        errors.append("Git worktree identity unavailable")
    if expected_worktree is not None:
        try:
            if root.resolve() != Path(expected_worktree).resolve():
                errors.append("worktree does not match expected worktree")
        except (OSError, ValueError):
            errors.append("expected worktree is unreadable")
    if expected_head and worktree.get("head") != expected_head:
        errors.append("HEAD does not match expected head")
    if expected_branch and worktree.get("branch") != expected_branch:
        errors.append("branch does not match expected branch")
    if expected_requirements_sha256 and requirements_hash != expected_requirements_sha256:
        errors.append(f"{GOAL_DOCUMENT_NAME} hash changed")

    task_scenes: dict[str, list[str]] = {"sheets_without_worktree": [], "worktrees_without_sheet": [], "uncommitted_sheets": [], "leftover_evidence": []}
    if root.is_dir():
        scene_warnings, scene_errors, task_scenes = _task_scene_facts(root)
        warnings.extend(scene_warnings)
        errors.extend(scene_errors)

    for error in errors:
        blockers.append({"class": "environment" if "command" in error or "Git" in error or "worktree" in error else "contract", "reason": error})
    next_actions: list[str] = []
    if any(task_scenes.values()):
        next_actions.append("reconcile existing task scenes before planning")
    if errors:
        next_actions.append("fix preflight blockers and rerun")
    result: dict[str, Any] = {
        "schema": 1,
        "status": "pass" if not errors else "blocked",
        "errors": errors,
        "blockers": blockers,
        "warnings": warnings,
        "requirements_sha256": requirements_hash,
        "worktree": worktree,
        "task_scenes": task_scenes,
        "artifacts": [],
        "next_actions": next_actions,
        "unverified": [] if not errors else ["planning dispatch", "task generation"],
    }
    if errors and root.is_dir():
        result["artifacts"] = _write_preflight_failure(root, result)
    else:
        _clear_stale_preflight_failure(root)
    return result


def _entity_id(item: Any, *, derive_from_path: bool = False) -> str | None:
    if isinstance(item, str) and item.strip():
        return item
    if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip():
        return item["id"]
    if derive_from_path:
        path = _entity_path(item)
        if path and _safe_entity_identifier(path):
            return path
    return None


def _entity_id_for_value(item: Any, *, derive_from_path: bool = False) -> str | None:
    return _entity_id(item, derive_from_path=derive_from_path)


def _entity_path(item: Any) -> str | None:
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return None
    for key in ("path", "file", "source", "reference", "uri"):
        if isinstance(item.get(key), str) and item[key].strip():
            return item[key]
    return None


def _validate_entity_list(
    value: Any,
    field: str,
    root: Path | None,
    errors: list[str],
    *,
    require_path: bool = False,
    derive_id_from_path: bool = False,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a non-empty array")
        return [], {}
    ids: list[str] = []
    records: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(value, 1):
        path = _entity_path(item)
        item_id = _entity_id(item)
        if item_id is None and derive_id_from_path and path:
            item_id = path
        if item_id is None or not (_safe_identifier(item_id) or (derive_id_from_path and _safe_entity_identifier(item_id))):
            errors.append(f"{field}[{index}] must contain a safe id")
            continue
        if item_id in records:
            errors.append(f"{field} ids must be unique: {item_id}")
            continue
        if require_path and path is None:
            errors.append(f"{field}[{index}] must contain a path")
        if path is not None:
            if root is not None:
                if not _safe_rel(root, path):
                    errors.append(f"{field} path is unsafe: {path}")
            elif not _safe_reference(path):
                errors.append(f"{field} path is unsafe: {path}")
        record = dict(item) if isinstance(item, dict) else {"id": item_id, "path": item}
        records[item_id] = record
        ids.append(item_id)
    return ids, records


def _not_applicable_reason(value: Any) -> str | None:
    if not isinstance(value, dict) or value.get("not_applicable") is not True:
        return None
    reason = value.get("reason")
    return reason.strip() if isinstance(reason, str) and reason.strip() else None


def _validate_chain(
    chain: Any,
    errors: list[str],
    *,
    required: bool = True,
    allow_not_applicable: bool = True,
) -> None:
    if not isinstance(chain, dict):
        errors.append("chain is required")
        return
    for name in CHAIN:
        value = chain.get(name)
        if isinstance(value, list):
            if not value:
                errors.append(f"chain.{name} must be non-empty or explicitly not-applicable")
                continue
            for index, reference in enumerate(value, 1):
                if isinstance(reference, str):
                    if not _safe_reference(reference):
                        errors.append(f"chain.{name}[{index}] is unsafe")
                elif isinstance(reference, dict):
                    ref = reference.get("path") or reference.get("ref") or reference.get("id")
                    if not _safe_identifier(ref) and not _safe_reference(ref):
                        errors.append(f"chain.{name}[{index}] is invalid")
                else:
                    errors.append(f"chain.{name}[{index}] is invalid")
        elif allow_not_applicable and _not_applicable_reason(value):
            continue
        elif value is None and not required:
            continue
        else:
            errors.append(f"chain.{name} must be non-empty or explicitly not-applicable")


def _acceptance_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("id") if isinstance(value.get("id"), str) else None
    return None


def _test_ref_path(value: Any) -> str | None:
    """Return the project-relative file path named by an acceptance test_ref.

    The accepted grammar is ``path/to/file.py: Class.method``; only the path
    before the first colon is position-bearing, and a bare path is valid.
    """
    if not isinstance(value, str):
        return None
    candidate = value.split(":", 1)[0].strip().replace("\\", "/")
    return candidate or None


def _covers_path(allowed: str, candidate: str) -> bool:
    allowed = allowed.strip().replace("\\", "/")
    if not allowed:
        return False
    if allowed.endswith("/"):
        return candidate.startswith(allowed)
    if allowed.endswith("/*"):
        return candidate.startswith(allowed[:-1])
    return candidate == allowed or candidate.startswith(allowed + "/")


def _shares_test_root(allowed: str, candidate: str) -> bool:
    """Return whether a resource path shares the test_ref's top-level directory."""
    normalized = allowed.strip().replace("\\", "/")
    root = candidate.split("/", 1)[0]
    return bool(root) and normalized.startswith(root + "/")


def _validate_test_ref_placement(
    declared: set[str],
    records: dict[str, dict[str, Any]],
    allowed_paths: list[str],
    errors: list[str],
    *,
    task_id: str,
) -> None:
    """Reject an acceptance test_ref that points outside the task's resources.

    The check only applies to a test file that shares a directory with a
    declared task resource: that is the case where the task claims ownership of
    the surrounding tree and the test must therefore live inside it.  A task
    that declares no resource in the test's directory makes no such claim, so
    its acceptance record is left to the other structural checks.
    """
    for test_id in sorted(declared):
        record = records.get(test_id)
        if not isinstance(record, dict):
            continue
        path = _test_ref_path(record.get("test_ref"))
        if path is None:
            continue
        claimed = [
            item for item in allowed_paths
            if _covers_path(item, path) or _shares_test_root(item, path)
        ]
        if not claimed:
            continue
        if any(_covers_path(item, path) for item in allowed_paths):
            continue
        errors.append(
            f"task {task_id} acceptance test {test_id} test_ref {path} is outside "
            "the task's allowed paths"
        )


def _validate_acceptance_records(
    records: Any,
    errors: list[str],
    *,
    field: str = "acceptance_tests",
    require_complete: bool = True,
) -> set[str]:
    if not isinstance(records, list) or not records:
        errors.append(f"{field} must be a non-empty array")
        return set()
    seen: set[str] = set()
    for index, item in enumerate(records, 1):
        identifier = _acceptance_id(item)
        if identifier is None or not ACCEPTANCE_ID_RE.fullmatch(identifier):
            errors.append(f"{field}[{index}] must use a full acceptance-test-* id")
            continue
        if identifier in seen:
            errors.append(f"duplicate acceptance test id: {identifier}")
            continue
        seen.add(identifier)
        if require_complete and isinstance(item, dict):
            for key in ("evidence_level", "test_ref", "command_ref"):
                if key not in item or not isinstance(item[key], (str, int)) or not str(item[key]).strip():
                    errors.append(f"{field}[{index}] missing complete field: {key}")
            level = item.get("evidence_level")
            if isinstance(level, bool) or not isinstance(level, int) or not 1 <= level <= 5:
                errors.append(f"{field}[{index}] evidence_level must be integer 1-5")
            for key in ("test_ref", "command_ref"):
                if isinstance(item.get(key), str) and PLACEHOLDER_RE.search(item[key]):
                    errors.append(f"{field}[{index}] {key} contains a placeholder")
        elif require_complete and isinstance(item, str):
            # A bare id can be used in a project-facts operation reference, but
            # not as a complete acceptance record.
            errors.append(f"{field}[{index}] is not a complete acceptance test")
    return seen


def _validate_operation_list(
    value: Any,
    errors: list[str],
    *,
    require_acceptance: bool,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    if not isinstance(value, list) or not value:
        errors.append("operations must be a non-empty array")
        return [], {}
    ids: list[str] = []
    records: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(value, 1):
        identifier = _entity_id(item)
        if identifier is None or not _safe_identifier(identifier):
            errors.append(f"operations[{index}] must contain a safe id")
            continue
        if identifier in records:
            errors.append(f"operations must be unique: {identifier}")
            continue
        record = dict(item) if isinstance(item, dict) else {"id": identifier}
        records[identifier] = record
        ids.append(identifier)
        tests = record.get("acceptance_tests")
        if require_acceptance:
            if not isinstance(tests, list) or not tests:
                errors.append(f"operation {identifier} must declare acceptance_tests")
            else:
                for test in tests:
                    test_id = _acceptance_id(test)
                    if test_id is None or not ACCEPTANCE_ID_RE.fullmatch(test_id):
                        errors.append("acceptance test ids must use full names")
        elif tests is not None:
            if not isinstance(tests, list) or not tests:
                errors.append(f"operation {identifier} acceptance_tests must be a non-empty array")
            else:
                for test in tests:
                    test_id = _acceptance_id(test)
                    if test_id is None or not ACCEPTANCE_ID_RE.fullmatch(test_id):
                        errors.append("acceptance test ids must use full names")
    return ids, records


def _validate_refs(
    records: Iterable[Any],
    known: set[str],
    field: str,
    errors: list[str],
    aliases: dict[str, str] | None = None,
) -> set[str]:
    if not isinstance(records, list):
        errors.append(f"{field} must be an array")
        return set()
    aliases = aliases or {}
    used: set[str] = set()
    for item in records:
        ref = _entity_id(item)
        if ref is None:
            errors.append(f"{field} contains an invalid reference")
            continue
        canonical = aliases.get(ref, ref)
        if canonical not in known:
            errors.append(f"{field} references unknown id: {ref}")
        else:
            used.add(canonical)
    return used


FACT_CATEGORIES = {"requirement", "project"}
FACT_SOURCE_FIELDS = ("source_id", "source_ref", "source")
FACT_STATUS = {"open", "resolved", "accepted", "rejected", "blocking", "non_blocking"}
DECISION_BLOCKER_STATUS = {"blocking", "resolved", "non_blocking"}
UNAUTHORIZED_DECISION_FIELDS = {"resolution", "decision", "resolved_by", "resolution_source", "auto_resolve"}


def _fact_source(record: dict[str, Any]) -> str | None:
    for field in FACT_SOURCE_FIELDS:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def normalize_facts(value: Any, *, planning_run_id: str | None = None) -> dict[str, Any]:
    """Normalize the mechanical planning-facts envelope without semantic inference."""
    if not isinstance(value, dict):
        return {"schema": 1, "planning_run_id": planning_run_id, "facts": [], "assumptions": [], "unknowns": [], "conflicts": [], "non_goals": [], "decision_blockers": []}
    result = {"schema": value.get("schema", 1), "planning_run_id": value.get("planning_run_id", planning_run_id)}
    for field in ("facts", "assumptions", "unknowns", "conflicts", "non_goals", "decision_blockers"):
        items = value.get(field, [])
        result[field] = items if isinstance(items, list) else []
    # Accept the existing requirement/project exports as input, preserving records.
    if not result["facts"]:
        for category, key in (("requirement", "requirements"), ("project", "resources")):
            for item in value.get(key, []) if isinstance(value.get(key), list) else []:
                record = dict(item) if isinstance(item, dict) else {"id": item}
                record.setdefault("category", category)
                result["facts"].append(record)
    for record in result["facts"]:
        if isinstance(record, dict):
            record.setdefault("category", record.get("type", "project"))
    return result


def validate_facts_model(value: Any, root: Path | None = None) -> list[str]:
    """Validate identity, sources, paths and blocking states only."""
    errors: list[str] = []
    model = normalize_facts(value)
    if model.get("schema") != 1:
        errors.append("schema must be 1")
    run_id = model.get("planning_run_id")
    if run_id is not None and not _safe_identifier(run_id):
        errors.append("planning_run_id must be a safe identifier")
    non_goals = model.get("non_goals")
    if not isinstance(non_goals, list) or not non_goals:
        errors.append("non_goals must be a non-empty array")
    elif any(not isinstance(item, str) or not item.strip() for item in non_goals):
        errors.append("non_goals must contain only non-empty strings")
    seen: set[str] = set()
    for field in ("facts", "assumptions", "unknowns", "conflicts", "decision_blockers"):
        records = model.get(field)
        if not isinstance(records, list):
            errors.append(f"{field} must be an array")
            continue
        for index, record in enumerate(records, 1):
            if not isinstance(record, dict):
                errors.append(f"{field}[{index}] must be an object")
                continue
            identifier = record.get("id")
            if not _safe_identifier(identifier):
                errors.append(f"{field}[{index}] must contain a safe id")
            elif identifier in seen:
                errors.append(f"duplicate fact id: {identifier}")
            else:
                seen.add(identifier)
            if field == "facts" and record.get("category") not in FACT_CATEGORIES:
                errors.append(f"facts[{index}] category must be requirement or project")
            if field == "assumptions" and record.get("status", "open") not in FACT_STATUS:
                errors.append(f"assumptions[{index}] has invalid status")
            if field == "unknowns" and record.get("status", "blocking") not in FACT_STATUS:
                errors.append(f"unknowns[{index}] has invalid status")
            if field == "decision_blockers":
                status = record.get("status")
                if status not in DECISION_BLOCKER_STATUS:
                    errors.append(f"decision_blockers[{index}] has invalid or missing status: {status!r}")
            if field in {"facts", "assumptions", "unknowns"} and _fact_source(record) is None:
                errors.append(f"{field}[{index}] must contain a source")
            unauthorized = sorted(UNAUTHORIZED_DECISION_FIELDS.intersection(record))
            if unauthorized:
                errors.append(f"{field}[{index}] contains unauthorized decision fields: {', '.join(unauthorized)}")
            path = record.get("path")
            if path is not None and (not isinstance(path, str) or (root is not None and not _safe_rel(root, path)) or (root is None and (not _safe_reference(path) or ".." in PurePosixPath(path.replace("\\\\", "/")).parts))):
                errors.append(f"{field}[{index}] path is unsafe")
            source_hash = record.get("source_sha256")
            if source_hash is not None and (not isinstance(source_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", source_hash)):
                errors.append(f"{field}[{index}] source_sha256 is invalid")
            if record.get("not_applicable") is True and not _not_applicable_reason(record):
                errors.append(f"{field}[{index}] not_applicable requires reason")
    return errors


def detect_fact_conflicts(value: Any, *, planning_run_id: str | None = None) -> dict[str, Any]:
    """Produce auditable conflicts; never choose between competing values."""
    model = normalize_facts(value, planning_run_id=planning_run_id)
    errors = validate_facts_model(model)
    conflicts = [dict(item) for item in model["conflicts"] if isinstance(item, dict)]
    by_entity: dict[str, list[dict[str, Any]]] = {}
    for record in model["facts"]:
        if isinstance(record, dict) and record.get("entity_id") is not None:
            by_entity.setdefault(str(record["entity_id"]), []).append(record)
    for entity, records in by_entity.items():
        values = {json.dumps(record.get("value"), sort_keys=True, ensure_ascii=True) for record in records if "value" in record}
        if len(values) > 1:
            conflicts.append({"id": f"conflict-{entity}", "entity_id": entity, "kind": "mutually-exclusive-values", "fact_ids": [r.get("id") for r in records], "status": "blocking", "decision_required": True, "next_actions": ["obtain product decision", "re-run facts validation"]})
    blockers = [dict(item) for item in model["decision_blockers"] if isinstance(item, dict)]
    blockers.extend({"id": c.get("id"), "kind": "conflict", "status": "blocking", "decision_required": True} for c in conflicts if c.get("status") == "blocking")
    blockers.extend({"id": item.get("id"), "kind": "unknown", "status": "blocking", "decision_required": True} for item in model["unknowns"] if isinstance(item, dict) and item.get("status", "blocking") in {"open", "blocking"} and item.get("not_applicable") is not True)
    blocking_blockers = [item for item in blockers if item.get("status") == "blocking"]
    blocked = bool(errors or blocking_blockers)
    return {"schema": 1, "planning_run_id": model.get("planning_run_id"), "status": "blocked" if blocked else "pass", "errors": errors, "facts": model["facts"], "assumptions": model["assumptions"], "unknowns": model["unknowns"], "conflicts": conflicts, "non_goals": model["non_goals"], "decision_blockers": blockers, "decision_required": bool(blockers), "next_actions": ["resolve decision blockers before planning"] if blocked else [], "unverified": ["semantic correctness"]}


def gate_facts_for_planning(value: Any, *, planning_run_id: str | None = None) -> dict[str, Any]:
    result = detect_fact_conflicts(value, planning_run_id=planning_run_id)
    result["planning_allowed"] = result["status"] == "pass"
    result["generation_allowed"] = result["planning_allowed"]
    result["dispatch_allowed"] = result["planning_allowed"]
    return result


def validate_requirement_facts(facts: dict[str, Any], root: Path | None = None) -> list[str]:
    """Validate requirement facts and their source/acceptance references."""
    errors: list[str] = []
    if not isinstance(facts, dict) or facts.get("schema") != 1:
        return ["schema must be 1"]
    source_ids, _sources = _validate_entity_list(
        facts.get("sources"), "sources", root, errors, require_path=True
    )
    requirement_ids, requirements = _validate_entity_list(
        facts.get("requirements"), "requirements", None, errors, require_path=False,
        derive_id_from_path=True,
    )
    if not requirement_ids:
        errors.append("requirements must not be empty")
    source_set = set(source_ids)
    for identifier, requirement in requirements.items():
        refs = requirement.get("source_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"requirement {identifier} must declare source_refs")
        else:
            _validate_refs(refs, source_set, f"requirement {identifier}.source_refs", errors)
    _operation_ids, operations = _validate_operation_list(
        facts.get("operations"), errors, require_acceptance=True
    )
    tests = facts.get("acceptance_tests")
    test_ids = _validate_acceptance_records(tests, errors, require_complete=True)
    for identifier, operation in operations.items():
        refs = operation.get("acceptance_tests")
        for test in refs if isinstance(refs, list) else []:
            test_id = _acceptance_id(test)
            if test_id and test_id not in test_ids:
                errors.append(f"operation {identifier} references unknown acceptance test: {test_id}")
    if "chain" in facts:
        _validate_chain(facts.get("chain"), errors)
    return errors


def validate_project_facts(facts: dict[str, Any], root: Path | None = None) -> list[str]:
    """Validate project-facts structure without making semantic judgments.

    String operation entries remain accepted for compatibility with older fact
    exports; binding those operations to complete acceptance tests is enforced by
    ``validate_requirement_facts`` and ``validate_task_plan``.
    """
    errors: list[str] = []
    if not isinstance(facts, dict) or facts.get("schema") != 1:
        return ["schema must be 1"]
    _source_ids, _sources = _validate_entity_list(
        facts.get("sources"), "sources", root, errors, require_path=True,
        derive_id_from_path=True,
    )
    _resource_ids, _resources = _validate_entity_list(
        facts.get("resources"), "resources", root, errors, require_path=True,
        derive_id_from_path=True,
    )

    # A structured operation must carry an acceptance binding.  Bare string
    # operations are retained as a compatibility representation for older
    # project-facts exports; task-plan validation remains the strict boundary.
    raw_operations = facts.get("operations")
    if isinstance(raw_operations, list):
        for index, operation in enumerate(raw_operations, 1):
            if isinstance(operation, dict) and not operation.get("acceptance_tests"):
                errors.append(f"operations[{index}] must declare acceptance_tests")
            elif isinstance(operation, dict) and not isinstance(operation.get("acceptance_tests"), list):
                errors.append(f"operations[{index}] acceptance_tests must be an array")
    _operation_ids, _operations = _validate_operation_list(
        facts.get("operations"), errors, require_acceptance=False
    )
    _validate_chain(facts.get("chain"), errors)
    if "acceptance_tests" in facts:
        _validate_acceptance_records(facts.get("acceptance_tests"), errors, require_complete=True)
    return errors


def _aliases_for_entities(value: list[Any]) -> tuple[set[str], dict[str, str]]:
    known: set[str] = set()
    aliases: dict[str, str] = {}
    for item in value:
        identifier = _entity_id(item)
        if identifier is None:
            continue
        known.add(identifier)
        if isinstance(item, dict):
            path = _entity_path(item)
            if path:
                aliases[path] = identifier
    return known, aliases


def validate_task_plan(
    plan: dict[str, Any],
    project_facts: dict[str, Any] | None = None,
    requirement_facts: dict[str, Any] | None = None,
) -> list[str]:
    """Validate task coverage, full operation tests, dependencies, and derivation."""
    errors: list[str] = []
    if not isinstance(plan, dict) or plan.get("schema") != 1:
        errors.append("schema must be 1")
        return errors
    for field in ("requirements", "resources", "operations", "tasks"):
        if not isinstance(plan.get(field), list) or not plan[field]:
            errors.append(f"{field} must be a non-empty array")
    non_goals = plan.get("non_goals")
    if not isinstance(non_goals, list) or not non_goals:
        errors.append("non_goals must be a non-empty array")
    elif any(not isinstance(item, str) or not item.strip() for item in non_goals):
        errors.append("non_goals must contain only non-empty strings")
    if project_facts is not None:
        errors.extend(f"project-facts: {error}" for error in validate_project_facts(project_facts))
    if requirement_facts is not None:
        errors.extend(f"requirement-facts: {error}" for error in validate_requirement_facts(requirement_facts))

    requirement_known, requirement_aliases = _aliases_for_entities(plan.get("requirements", []))
    resource_known, resource_aliases = _aliases_for_entities(plan.get("resources", []))
    operation_ids, operation_records = _validate_operation_list(
        plan.get("operations"), errors, require_acceptance=True
    )
    operation_known = set(operation_ids)
    operation_acceptance_ids: set[str] = set()
    for operation in operation_records.values():
        tests = operation.get("acceptance_tests")
        for item in tests if isinstance(tests, list) else []:
            test_id = _acceptance_id(item)
            if test_id:
                operation_acceptance_ids.add(test_id)
    top_level_tests = plan.get("acceptance_tests")
    if "acceptance_tests" not in plan:
        errors.append("acceptance_tests must declare complete top-level records")
        complete_ids = set()
    else:
        complete_ids = _validate_acceptance_records(top_level_tests, errors, require_complete=True)
        for operation_id, operation in operation_records.items():
            for item in operation.get("acceptance_tests", []):
                test_id = _acceptance_id(item)
                if test_id and test_id not in complete_ids:
                    errors.append(f"operation {operation_id} references unknown acceptance test: {test_id}")
    for operation_id, operation in operation_records.items():
        tests = operation.get("acceptance_tests")
        if not isinstance(tests, list) or not tests:
            continue
        if not any(_acceptance_id(item) in complete_ids for item in tests):
            errors.append(f"operation {operation_id} has no complete acceptance test")
        resources = operation.get("resources")
        if not isinstance(resources, list) or not resources:
            errors.append(f"operation {operation_id} must declare resources")
        else:
            mode = "single" if len(resources) == 1 else "batch"
            declared_mode = operation.get("resource_mode")
            if declared_mode is None:
                errors.append(
                    f"operation {operation_id} must declare resource_mode "
                    f"single or batch ({len(resources)} resource(s); expected {mode})"
                )
            elif declared_mode != mode:
                errors.append(
                    f"operation {operation_id} resource_mode {declared_mode} does not match "
                    f"{len(resources)} resource(s); expected {mode}"
                )
            _validate_refs(resources, resource_known, f"operation {operation_id}.resources", errors, resource_aliases)

    plan_risk = plan.get("risk", "medium")
    if plan_risk not in RISK_LEVELS:
        errors.append(
            f"plan risk must be one of {', '.join(RISK_LEVELS)}; got {plan_risk!r}"
        )
    plan_project_type = plan.get("project_type", DEFAULT_PROJECT_TYPE)
    if plan_project_type not in PROJECT_TYPES:
        errors.append(
            f"plan project_type must be one of {', '.join(PROJECT_TYPES)}; "
            f"got {plan_project_type!r}"
        )
    acceptance_levels: dict[str, Any] = {
        item.get("id"): item.get("evidence_level")
        for item in plan.get("acceptance_tests", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    tasks = plan.get("tasks") if isinstance(plan.get("tasks"), list) else []
    task_ids: list[str] = []
    task_map: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(tasks, 1):
        if not isinstance(task, dict):
            errors.append(f"task {index} must be an object")
            continue
        identifier = task.get("id")
        if not _safe_identifier(identifier):
            errors.append(f"task {index} has invalid id")
            continue
        if identifier in task_map:
            errors.append(f"task ids must be unique: {identifier}")
            continue
        task_ids.append(identifier)
        task_map[identifier] = task
        task_type = task.get("type")
        if task_type not in TASK_TYPES:
            errors.append(f"task {identifier} has invalid task type")
        floor = evidence_floor(plan_risk, plan_project_type, task_type)
        declared = {
            test_id
            for operation_id in task.get("operations", [])
            for test_id in operation_records.get(operation_id, {}).get("acceptance_tests", [])
        }
        accepted_records = {
            item.get("id"): item
            for item in plan.get("acceptance_tests", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        try:
            task_allowed_paths = _task_allowed_paths(task)
        except ValueError:
            task_allowed_paths = []
        resource_paths: dict[str, str] = {}
        for source in (plan, project_facts, requirement_facts):
            if not isinstance(source, dict):
                continue
            for entity in source.get("resources", []) or []:
                if (
                    isinstance(entity, dict)
                    and isinstance(entity.get("id"), str)
                    and isinstance(entity.get("path"), str)
                ):
                    resource_paths.setdefault(entity["id"], entity["path"])
        task_allowed_paths = [
            resource_paths.get(item, item) for item in task_allowed_paths
        ]
        if task_allowed_paths:
            _validate_test_ref_placement(
                declared, accepted_records, task_allowed_paths, errors, task_id=identifier
            )
        if floor is not None:
            for test_id in sorted(declared):
                level = acceptance_levels.get(test_id)
                if isinstance(level, bool) or not isinstance(level, int):
                    continue
                if level < floor:
                    errors.append(
                        f"task {identifier} acceptance test {test_id} evidence_level "
                        f"{level} is below the required floor {floor}"
                    )
        for field in ("requirements", "resources", "operations"):
            if not isinstance(task.get(field), list):
                errors.append(f"task {identifier} missing {field}")
        if task_type in {"vertical-feature", "repair"}:
            chain = task.get("chain")
            if not isinstance(chain, dict):
                errors.append(f"task {identifier} chain is incomplete")
            else:
                _validate_chain(chain, errors, required=True, allow_not_applicable=False)
        elif "chain" in task:
            _validate_chain(task.get("chain"), errors, required=False)
        depends = task.get("depends_on", [])
        if not isinstance(depends, list):
            errors.append(f"task {identifier} depends_on must be an array")
        else:
            if len(depends) != len(set(depends)):
                errors.append(f"task {identifier} has duplicate dependencies")
            for dependency in depends:
                if dependency not in task_map and dependency not in {other.get("id") for other in tasks if isinstance(other, dict)}:
                    errors.append(f"task {identifier} has invalid dependency")
        parent = task.get("parent_task_id")
        derived_from = task.get("derived_from")
        if task_type == "derived":
            if not _safe_identifier(parent):
                errors.append(f"derived task {identifier} requires parent_task_id")
            elif parent not in {other.get("id") for other in tasks if isinstance(other, dict)}:
                errors.append(f"derived task {identifier} has invalid parent_task_id")
            if isinstance(derived_from, dict):
                relation_id = derived_from.get("task_id") or derived_from.get("parent_task_id")
                if relation_id != parent:
                    errors.append(f"derived task {identifier} has inconsistent derived_from")
            elif derived_from is not None and derived_from != parent:
                errors.append(f"derived task {identifier} has inconsistent derived_from")
        elif parent is not None or derived_from is not None:
            errors.append(f"non-derived task {identifier} cannot declare a parent")

    known_task_ids = set(task_ids)
    graph: dict[str, list[str]] = {}
    for identifier, task in task_map.items():
        depends = task.get("depends_on", [])
        graph[identifier] = [d for d in depends if isinstance(d, str)] if isinstance(depends, list) else []
        for dependency in graph[identifier]:
            if dependency not in known_task_ids:
                # The specific invalid dependency error was emitted above.
                continue
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        cycle = any(visit(dep) for dep in graph.get(node, []) if dep in graph)
        visiting.remove(node)
        visited.add(node)
        return cycle

    if any(visit(node) for node in graph):
        errors.append("dependency cycle")

    covered_requirements: set[str] = set()
    covered_resources: set[str] = set()
    covered_operations: set[str] = set()
    for identifier, task in task_map.items():
        covered_requirements.update(_validate_refs(task.get("requirements"), requirement_known, f"task {identifier}.requirements", errors, requirement_aliases))
        covered_resources.update(_validate_refs(task.get("resources"), resource_known, f"task {identifier}.resources", errors, resource_aliases))
        covered_operations.update(_validate_refs(task.get("operations"), operation_known, f"task {identifier}.operations", errors))
    if requirement_known - covered_requirements:
        errors.append("uncovered requirements: " + ", ".join(sorted(requirement_known - covered_requirements)))
    if resource_known - covered_resources:
        errors.append("uncovered resources: " + ", ".join(sorted(resource_known - covered_resources)))
    if operation_known - covered_operations:
        errors.append("uncovered operations: " + ", ".join(sorted(operation_known - covered_operations)))
    return errors


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    return value


def compare_task_plan_contract(
    task_plan: dict[str, Any],
    task_sheet: Path,
    *,
    root: Path | None = None,
    expected_requirements_sha256: str | None = None,
    expected_run_id: str | None = None,
) -> dict[str, Any]:
    """Compare one planned task with its generated schema-2 task sheet.

    This is deliberately read-only and fail-closed: the plan and sheet must both
    validate, identify exactly one task, and agree on every mechanically derived
    field before the result can be used for freeze or dispatch.
    """
    errors: list[dict[str, Any]] = []
    plan_errors = validate_task_plan(task_plan)
    errors.extend({"field": "task_plan", "reason": error, "source": "task-plan"} for error in plan_errors)
    contract, contract_errors = load_contract(Path(task_sheet))
    errors.extend({"field": "task_sheet", "reason": error, "source": str(task_sheet)} for error in contract_errors)
    if contract is None:
        return {"schema": 1, "status": "fail", "task_id": None, "conflicts": errors,
                "errors": [item["reason"] for item in errors], "next_actions": ["do not freeze or dispatch"]}

    task_id = contract.get("task_id")
    tasks = [item for item in task_plan.get("tasks", []) if isinstance(item, dict) and item.get("id") == task_id]
    if len(tasks) != 1:
        errors.append({"field": "task_id", "reason": "task sheet must map to exactly one task-plan task", "source": "task-plan/task-sheet"})
        return {"schema": 1, "status": "fail", "task_id": task_id, "conflicts": errors,
                "errors": [item["reason"] for item in errors], "next_actions": ["do not freeze or dispatch"]}
    task = tasks[0]
    task_operation_ids = task.get("operations", [])
    operations = [item for item in task_plan.get("operations", []) if isinstance(item, dict) and item.get("id") in task_operation_ids]
    referenced_test_ids = {test_id for operation in operations for test_id in operation.get("acceptance_tests", [])}
    expected_tests = [item for item in task_plan.get("acceptance_tests", []) if isinstance(item, dict) and item.get("id") in referenced_test_ids]

    def expected_operation(item: dict[str, Any]) -> dict[str, Any]:
        record: dict[str, Any] = {
            "id": item.get("id"),
            "kind": item.get("kind", "execute"),
            "scope": item.get("scope", "task"),
        }
        if contract.get("schema") in {3, 4}:
            resources = _operation_resources(item, task)
            record["resources"] = resources
            record["resource_mode"] = "single" if len(resources) == 1 else "batch"
        elif "resources" in item:
            record["resources"] = item.get("resources", [])
        record["acceptance_tests"] = item.get("acceptance_tests", [])
        return record

    try:
        expected = {
            "task_type": task.get("type"),
            "requirements": task.get("requirements", []),
            "resources": task.get("resources", []),
            "operations": [expected_operation(item) for item in operations],
            "chain": _planning_chain(task.get("chain")),
            "dependencies": task.get("depends_on", []),
            "acceptance_tests": expected_tests,
            "allowed_paths": _task_allowed_paths(task),
        }
        if contract.get("schema") in {3, 4}:
            expected["non_goals"] = [
                item for item in task_plan.get("non_goals", [])
                if isinstance(item, str) and item.strip()
            ]
    except ValueError as error:
        errors.append({"field": "operations", "reason": str(error), "source": "task-plan"})
        return {"schema": 1, "status": "fail", "task_id": task_id, "conflicts": errors,
                "errors": [item["reason"] for item in errors], "next_actions": ["do not freeze or dispatch"]}
    actual = {key: contract.get(key) for key in expected}
    for field in expected:
        if _canonical(actual[field]) != _canonical(expected[field]):
            errors.append({"field": field, "reason": f"{field} differs between task-plan and task sheet", "source": "task-plan/task-sheet", "expected": expected[field], "actual": actual[field]})

    expected_schema = contract.get("schema")
    if expected_schema not in {2, 3, 4}:
        errors.append({"field": "schema", "reason": "task sheet contract schema must be 2, 3 or 4", "source": "task-sheet"})

    doc_field = "goal" if expected_schema == 4 else "implement_plan"
    default_doc = GOAL_DOCUMENT_NAME if expected_schema == 4 else LEGACY_PLAN_DOCUMENT_NAME
    requirements_doc = contract.get(doc_field)
    if not isinstance(requirements_doc, dict):
        errors.append({"field": doc_field, "reason": f"{doc_field} must be an object", "source": "task-sheet"})
    else:
        plan_root = Path(root) if root is not None else Path(task_sheet).resolve().parent.parent.parent
        plan_path = plan_root / str(requirements_doc.get("path", default_doc))
        try:
            plan_path.read_text(encoding="utf-8")
            live_hash = _sha256(plan_path)
        except (OSError, UnicodeError):
            live_hash = None
            errors.append({"field": f"{doc_field}.path", "reason": f"{default_doc} is missing or unreadable", "source": f"{default_doc}/task-sheet"})
        if expected_requirements_sha256 is not None and requirements_doc.get("sha256") != expected_requirements_sha256:
            errors.append({"field": f"{doc_field}.sha256", "reason": f"{default_doc} hash differs from expected hash", "source": "task-sheet"})
        if live_hash is not None and requirements_doc.get("sha256") != live_hash:
            errors.append({"field": f"{doc_field}.sha256", "reason": f"{default_doc} hash drift", "source": f"{default_doc}/task-sheet"})
        if expected_run_id is not None and requirements_doc.get("planning_run_id") != expected_run_id:
            errors.append({"field": f"{doc_field}.planning_run_id", "reason": "planning run id differs from expected run id", "source": "task-sheet"})
    status = "pass" if not errors else "fail"
    return {"schema": 1, "status": status, "task_id": task_id, "conflicts": errors,
            "errors": [item["reason"] for item in errors], "next_actions": [] if status == "pass" else ["do not freeze or dispatch"]}


def task_plan_contract_consistency(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return compare_task_plan_contract(*args, **kwargs)


def _planning_run_directory(root: Path, run_id: str) -> Path:
    if not _safe_identifier(run_id):
        raise ValueError("invalid planning run id")
    directory = (root / ".pipeline" / "planning" / run_id).resolve()
    if not directory.is_relative_to(root.resolve()):
        raise ValueError("planning audit directory escapes project root")
    return directory


_PLANNING_PHASES = ("started", "preflight", "planned", "generated", "finalized")
_PLANNING_TERMINAL = {"finalized", "failed", "blocked", "interrupted", "conflict"}


def _planning_identity(root: Path, run_id: str) -> dict[str, Any]:
    root = Path(root).resolve()
    plan, sync_error = sync_goal_document(root)
    facts, errors = _worktree_facts(root)
    if errors or sync_error or not plan.is_file():
        raise ValueError("planning run identity unavailable")
    return {
        "run_id": run_id,
        "root": str(root),
        "head": facts.get("head"),
        "branch": facts.get("branch"),
        "requirements_sha256": _sha256(plan),
    }


def _write_planning_json(path: Path, value: dict[str, Any], *, create_only: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if create_only and path.exists():
        raise FileExistsError(str(path))
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


def _project_approval_mode(root: Path) -> str:
    """Read the project-level approval default without creating anything."""
    path = Path(root) / ".pipeline" / "config.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "automatic"
    if isinstance(value, dict) and value.get("approval_mode") in {"automatic", "manual"}:
        return value["approval_mode"]
    return "automatic"


def _recorded_approval_mode(root: Path, run_id: str) -> str | None:
    """Return the approval mode recorded in a run's lifecycle state, if any."""
    try:
        _directory, state = _read_planning_state(Path(root), run_id)
    except (OSError, ValueError):
        return None
    value = state.get("approval_mode")
    return value if value in {"automatic", "manual"} else None


def _read_planning_state(root: Path, run_id: str) -> tuple[Path, dict[str, Any]]:
    directory = _planning_run_directory(Path(root), run_id)
    path = directory / "lifecycle.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("planning lifecycle state is unreadable") from error
    if not isinstance(value, dict) or value.get("run_id") != run_id:
        raise ValueError("planning lifecycle identity is invalid")
    return directory, value


def _planning_identity_matches(root: Path, state: dict[str, Any]) -> list[str]:
    try:
        live = _planning_identity(Path(root), str(state.get("run_id")))
    except (OSError, ValueError):
        return ["live planning identity unavailable"]
    return [field for field in ("root", "head", "branch", "requirements_sha256") if state.get(field) != live.get(field)]


def planning_run_start(root: Path, run_id: str | None = None, *, approval_mode: str | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    if run_id is not None:
        try:
            recorded = _recorded_approval_mode(root, run_id)
        except (OSError, ValueError):
            recorded = None
        if recorded is not None:
            # An already recorded run keeps its own approval policy; a missing
            # or unreadable record silently falls back to the project default.
            approval_mode = approval_mode or recorded
    if approval_mode is None:
        approval_mode = _project_approval_mode(root)
    if approval_mode not in {"automatic", "manual"}:
        return {"status": "blocked", "errors": ["invalid approval_mode"], "artifacts": [], "next_actions": []}
    if run_id is None:
        run_id = f"planning-{time.time_ns()}"
    try:
        identity = _planning_identity(root, run_id)
        directory = _planning_run_directory(root, run_id)
        # The lifecycle state is a process record, not a planning product: it is
        # retained for interruption, conflict and failure recovery.
        state = {"schema": 1, **identity, "approval_mode": approval_mode, "phase": "started", "status": "active", "history": [{"phase": "started", "status": "active"}], "artifacts": [], "errors": [], "next_actions": ["preflight"]}
        _write_planning_json(directory / "lifecycle.json", state, create_only=True)
        return {"status": "pass", "run_id": run_id, "phase": "started", "identity": identity, "artifacts": [str(directory / "lifecycle.json")], "errors": [], "next_actions": ["preflight"]}
    except FileExistsError:
        return {"status": "blocked", "run_id": run_id, "errors": ["planning run already exists"], "artifacts": [], "next_actions": ["recover"]}
    except (OSError, ValueError) as error:
        return {"status": "blocked", "run_id": run_id, "errors": [f"{type(error).__name__}: {error}"], "artifacts": [], "next_actions": ["fix identity and retry"]}


def planning_run_transition(root: Path, run_id: str, phase: str, *, status: str = "active", error: str | None = None) -> dict[str, Any]:
    if phase not in _PLANNING_PHASES or status not in {"active", "failed", "blocked", "interrupted", "conflict"}:
        return {"status": "blocked", "run_id": run_id, "errors": ["invalid phase or status"], "artifacts": [], "next_actions": []}
    try:
        directory, state = _read_planning_state(root, run_id)
        drift = _planning_identity_matches(root, state)
        if drift:
            state.update({"status": "conflict", "phase": "conflict", "errors": ["identity drift: " + ", ".join(drift)]})
            _write_planning_json(directory / "lifecycle.json", state)
            return {"status": "blocked", "run_id": run_id, "phase": "conflict", "errors": state["errors"], "artifacts": [str(directory / "lifecycle.json")], "next_actions": ["restore bound identity; do not resume"]}
        current = state.get("phase")
        if status == "active" and (current not in _PLANNING_PHASES or _PLANNING_PHASES.index(phase) != _PLANNING_PHASES.index(current) + 1):
            return {"status": "blocked", "run_id": run_id, "phase": current, "errors": ["invalid lifecycle transition"], "artifacts": [str(directory / "lifecycle.json")], "next_actions": ["recover"]}
        state["phase"], state["status"] = phase, status
        if error:
            state.setdefault("errors", []).append(error)
        state.setdefault("history", []).append({"phase": phase, "status": status, "error": error})
        state["next_actions"] = [] if status != "active" and phase in _PLANNING_TERMINAL else (["finalize"] if phase == "generated" else ["next phase"])
        _write_planning_json(directory / "lifecycle.json", state)
        return {"status": "pass" if status == "active" else status, "run_id": run_id, "phase": phase, "artifacts": [str(directory / "lifecycle.json")], "errors": state.get("errors", []), "next_actions": state["next_actions"]}
    except (OSError, ValueError) as error:
        return {"status": "blocked", "run_id": run_id, "errors": [f"{type(error).__name__}: {error}"], "artifacts": [], "next_actions": ["recover"]}


def _purge_successful_planning_run(root: Path, run_id: str) -> None:
    """Remove a successful run's process records, leaving only task sheets."""
    try:
        directory = _planning_run_directory(Path(root), run_id)
    except (OSError, ValueError):
        return
    if not directory.is_dir():
        return
    shutil.rmtree(directory, ignore_errors=True)
    planning_root = directory.parent
    try:
        if planning_root.is_dir() and not any(planning_root.iterdir()):
            planning_root.rmdir()
    except OSError:
        pass


def planning_run_finalize(root: Path, run_id: str, *, success: bool, approval: bool = False) -> dict[str, Any]:
    try:
        candidate = _planning_run_directory(Path(root), run_id)
    except (OSError, ValueError) as error:
        return {"status": "blocked", "run_id": run_id, "errors": [f"{type(error).__name__}: {error}"], "artifacts": [], "next_actions": ["recover"]}
    if success and not candidate.is_dir():
        # A successful run leaves only the frozen task sheets, so a repeated
        # finalize is idempotent without any retained lifecycle state.
        return {"schema": 1, "run_id": run_id, "status": "finalized", "requirements_sha256": None, "artifacts": [], "errors": [], "next_actions": [], "phase": "finalized"}
    try:
        directory, state = _read_planning_state(root, run_id)
        drift = _planning_identity_matches(root, state)
        if drift:
            return planning_run_transition(root, run_id, "conflict", status="conflict", error="identity drift: " + ", ".join(drift))
        if state.get("status") == "finalized":
            result_path = directory / "result.json"
            if result_path.is_file():
                try:
                    existing = json.loads(result_path.read_text(encoding="utf-8"))
                    if isinstance(existing, dict):
                        return existing
                except (OSError, UnicodeError, json.JSONDecodeError):
                    pass
            return {"schema": 1, "run_id": run_id, "status": "finalized", "requirements_sha256": state.get("requirements_sha256"), "artifacts": [], "errors": [], "next_actions": [], "phase": "finalized"}
        if success and state.get("phase") != "generated":
            return {"status": "blocked", "run_id": run_id, "phase": state.get("phase"), "errors": ["successful finalization requires generated phase"], "artifacts": [str(directory / "lifecycle.json")], "next_actions": ["transition to generated before finalizing"]}
        if success and state.get("approval_mode") == "manual" and not approval:
            return {"status": "blocked", "run_id": run_id, "errors": ["manual approval required"], "artifacts": [str(directory / "lifecycle.json")], "next_actions": ["approve then finalize"]}
        phase = "finalized" if success else "failed"
        result = {
            "schema": 1,
            "run_id": run_id,
            "status": "finalized" if success else "failed",
            "requirements_sha256": state["requirements_sha256"],
            "artifacts": [],
            "errors": [],
            "next_actions": [],
            "phase": phase,
        }
        if success:
            # A successful planning run leaves only the frozen task sheets.  The
            # lifecycle, stage and dispatch records are process artifacts and are
            # removed here; failures keep the full audit trail below.
            _purge_successful_planning_run(root, run_id)
            return result
        state.update({"phase": phase, "status": phase, "result": "fail", "next_actions": []})
        state.setdefault("history", []).append({"phase": phase, "status": phase})
        _write_planning_json(directory / "lifecycle.json", state)
        result["artifacts"] = ["lifecycle.json"]
        _write_planning_json(directory / "result.json", result)
        return result
    except (OSError, ValueError) as error:
        return {"status": "blocked", "run_id": run_id, "errors": [f"{type(error).__name__}: {error}"], "artifacts": [], "next_actions": ["recover"]}


def planning_run_recover(root: Path, run_id: str) -> dict[str, Any]:
    try:
        directory = _planning_run_directory(Path(root), run_id)
    except (OSError, ValueError) as error:
        return {"status": "blocked", "run_id": run_id, "errors": [f"{type(error).__name__}: {error}"], "artifacts": [], "next_actions": ["inspect retained failure evidence"]}
    if not directory.is_dir():
        # A successful planning run leaves only the frozen task sheets; there is
        # no lifecycle state left to recover.
        return {"status": "finalized", "run_id": run_id, "phase": "finalized", "identity": {}, "artifacts": [], "errors": [], "next_actions": []}
    try:
        directory, state = _read_planning_state(root, run_id)
        drift = _planning_identity_matches(root, state)
        if drift:
            return {"status": "blocked", "run_id": run_id, "phase": "conflict", "errors": ["identity drift: " + ", ".join(drift)], "artifacts": [str(directory / "lifecycle.json")], "next_actions": ["do not resume"]}
        return {"status": "pass", "run_id": run_id, "phase": state.get("phase"), "identity": {key: state.get(key) for key in ("root", "head", "branch", "requirements_sha256")}, "artifacts": [str(directory / name) for name in ("lifecycle.json", "result.json") if (directory / name).is_file()], "errors": state.get("errors", []), "next_actions": state.get("next_actions", [])}
    except (OSError, ValueError) as error:
        return {"status": "blocked", "run_id": run_id, "errors": [f"{type(error).__name__}: {error}"], "artifacts": [], "next_actions": ["inspect retained failure evidence"]}


def _planning_chain(chain: Any) -> dict[str, Any]:
    if isinstance(chain, dict) and any(chain.get(name) for name in CHAIN):
        return chain
    return {
        name: {
            "not_applicable": True,
            "reason": "this task declares no chain reference for this phase",
        }
        for name in CHAIN
    }


def _not_applicable_chain() -> dict[str, Any]:
    return _planning_chain(None)


def _operation_resources(operation: dict[str, Any], task: dict[str, Any]) -> list[str]:
    resources = operation.get("resources")
    if resources is None:
        resources = task.get("resources")
    if not isinstance(resources, list) or not resources:
        raise ValueError(
            f"operation {operation.get('id')} declares no resources; "
            "declare resources on the operation or its task"
        )
    resolved = [item for item in resources if isinstance(item, str) and item.strip()]
    if not resolved:
        raise ValueError(
            f"operation {operation.get('id')} declares no usable resources; "
            "declare non-empty resource ids on the operation or its task"
        )
    return resolved


def _task_allowed_paths(task: dict[str, Any]) -> list[str]:
    resources = task.get("resources")
    if not isinstance(resources, list) or not resources:
        raise ValueError(
            f"task {task.get('id')} declares no resources; allowed_paths cannot be derived"
        )
    paths = [str(item).replace("\\", "/") for item in resources if isinstance(item, str) and item.strip()]
    if not paths:
        raise ValueError(
            f"task {task.get('id')} declares no usable resources; allowed_paths cannot be derived"
        )
    return paths


def _task_forbidden_paths(task: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    """Derive forbidden_paths so they never contradict the task's own scope.

    ``.pipeline/** existing history`` guards the retained evidence history, so a
    task that already owns resources inside ``.pipeline/`` must not carry it.
    """
    forbidden = [GOAL_DOCUMENT_NAME, LEGACY_PLAN_DOCUMENT_NAME, "IDEA.md"]
    candidates: list[str] = []
    for value in task.get("resources") or []:
        if isinstance(value, str):
            candidates.append(value)
    operation_ids = task.get("operations") or []
    for operation in plan.get("operations", []) or []:
        if not isinstance(operation, dict) or operation.get("id") not in operation_ids:
            continue
        for value in operation.get("resources") or []:
            if isinstance(value, str):
                candidates.append(value)
    for entity in plan.get("resources", []) or []:
        if isinstance(entity, dict):
            identifier, path = entity.get("id"), entity.get("path")
            if isinstance(identifier, str) and isinstance(path, str) and identifier in candidates:
                candidates.append(path)
    touches_pipeline = any(
        normalized in {".pipeline"} or normalized.startswith(".pipeline/")
        for normalized in (candidate.replace("\\", "/") for candidate in candidates)
    )
    if not touches_pipeline:
        forbidden.append(".pipeline/** existing history")
    return forbidden


def _task_sheet_text(
    task: dict[str, Any],
    plan: dict[str, Any],
    requirements_sha256: str,
    run_id: str,
    *,
    assumptions: list[Any] | None = None,
    unknowns: list[Any] | None = None,
) -> str:
    task_id = task["id"]
    task_type = task["type"]
    operations = [item for item in plan.get("operations", []) if isinstance(item, dict) and item.get("id") in task.get("operations", [])]
    operation_ids = {item.get("id") for item in operations}
    tests = [item for item in plan.get("acceptance_tests", []) if isinstance(item, dict) and any(item.get("id") in op.get("acceptance_tests", []) for op in operations)]
    if not tests:
        raise ValueError(
            f"task {task_id} has no bound acceptance test; every operation must reference a declared acceptance test"
        )
    non_goals = [item for item in plan.get("non_goals", []) if isinstance(item, str) and item.strip()]
    if not non_goals:
        raise ValueError(
            f"task {task_id} has no non_goals; declare explicit non-goal sentences in the task plan"
        )
    contract = {
        "schema": 4,
        "task_id": task_id,
        "task_type": task_type,
        "goal": {"path": GOAL_DOCUMENT_NAME, "sha256": requirements_sha256, "planning_run_id": run_id},
        "risk": plan.get("risk", "medium"),
        "project_type": plan.get("project_type", DEFAULT_PROJECT_TYPE),
        "non_goals": non_goals,
        "allowed_paths": _task_allowed_paths(task),
        "forbidden_paths": _task_forbidden_paths(task, plan),
        "requirements": task.get("requirements", []),
        "resources": task.get("resources", []),
        "operations": [
            {
                "id": item.get("id"),
                "kind": item.get("kind", "execute"),
                "scope": item.get("scope", "task"),
                "resources": _operation_resources(item, task),
                "resource_mode": "single" if len(_operation_resources(item, task)) == 1 else "batch",
                "acceptance_tests": item.get("acceptance_tests", []),
            }
            for item in operations
        ],
        "chain": _planning_chain(task.get("chain")),
        "acceptance_tests": tests,
        "dependencies": task.get("depends_on", []),
        "required_evidence_levels": sorted({item.get("evidence_level") for item in tests if isinstance(item.get("evidence_level"), int)}) or [1],
        "assumptions": list(assumptions or []),
        "unknowns": list(unknowns or []),
    }
    if task_type == "prerequisite":
        reason = task.get("non_user_completion_reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(
                f"task {task_id} is prerequisite but declares no non_user_completion_reason in the task plan"
            )
        contract["non_user_completion_reason"] = reason
    lines = [f"# {task_id}：冻结任务单", "", f"<!-- Task ID: {task_id} -->", "<!-- Generated from task-plan; contract fields are mechanically derived. -->", "", "```pipeline-contract", json.dumps(contract, ensure_ascii=True, indent=2), "```", "", "## 任务身份", "", f"- 任务类型：`{task_type}`", f"- planning-run-id：`{run_id}`", f"- goal SHA-256：`{requirements_sha256}`", "- 状态：未开始", "", "## 依赖与范围", "", "### 允许修改", ""]
    lines.extend(f"- `{item}`" for item in contract["allowed_paths"])
    lines.extend(["", "### 明确不改", "", f"- `{GOAL_DOCUMENT_NAME}`", f"- `{LEGACY_PLAN_DOCUMENT_NAME}`", "- `IDEA.md`", "- 已有任务单和历史规划证据", "", "## 任务计划映射", "", f"- 需求：{json.dumps(task.get('requirements', []), ensure_ascii=True)}", f"- 资源：{json.dumps(task.get('resources', []), ensure_ascii=True)}", f"- 操作：{json.dumps(sorted(operation_ids), ensure_ascii=True)}", f"- 依赖：{json.dumps(task.get('depends_on', []), ensure_ascii=True)}", "", "## 验收测试", ""])
    for index, test in enumerate(tests, 1):
        lines.extend([f"### 验收测试{index}：{test.get('id')}", "", f"- 测试：`{test.get('test_ref')}`", f"- 命令：`{test.get('command_ref')}`", f"- 证据等级：{test.get('evidence_level')}", ""])
    return "\n".join(lines) + "\n"


def generate_task_sheets(
    root: Path,
    planning_run_id: str,
    project_facts: dict[str, Any],
    requirement_facts: dict[str, Any],
    task_plan: dict[str, Any],
    *,
    expected_requirements_sha256: str | None = None,
    assumptions: list[Any] | None = None,
    unknowns: list[Any] | None = None,
) -> dict[str, Any]:
    """Generate all task sheets atomically after mechanical planning checks."""
    root = Path(root).resolve()
    _planning_run_directory(root, planning_run_id)
    result: dict[str, Any] = {"schema": 1, "command": "planning.generate-task-sheets", "status": "blocked", "run_id": planning_run_id, "planning_run_id": planning_run_id, "task_id": None, "task_ids": [], "artifacts": [], "errors": [], "next_actions": []}
    try:
        preflight = planning_preflight(root, expected_requirements_sha256=expected_requirements_sha256)
        errors = list(preflight.get("errors", []))
        plan_path = root / GOAL_DOCUMENT_NAME
        requirements_sha256 = preflight.get("requirements_sha256")
        errors.extend(f"project-facts: {error}" for error in validate_project_facts(project_facts, root))
        errors.extend(f"requirement-facts: {error}" for error in validate_requirement_facts(requirement_facts, root))
        errors.extend(validate_task_plan(task_plan, project_facts, requirement_facts))
        tasks = task_plan.get("tasks", []) if isinstance(task_plan, dict) else []
        task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
        if len(task_ids) != len(set(task_ids)):
            errors.append("task ids must be unique")
        if requirements_sha256 is None or not plan_path.is_file():
            errors.append(f"{GOAL_DOCUMENT_NAME} hash unavailable")
        if errors:
            result["errors"] = errors
            result["next_actions"] = ["fix planning inputs and rerun"]
            return result
        destinations = [root / "docs" / "tasks" / f"{task_id}.md" for task_id in task_ids]
        for destination in destinations:
            if destination.exists() or destination.is_symlink():
                errors.append(f"task sheet already exists: {destination.relative_to(root).as_posix()}")
            if not _safe_rel(root, destination.relative_to(root).as_posix()):
                errors.append("task sheet output path is unsafe")
        if errors:
            result["errors"] = errors
            result["next_actions"] = ["remove conflicts without overwriting existing task sheets"]
            return result
        contents = [
            _task_sheet_text(
                task,
                task_plan,
                str(requirements_sha256),
                planning_run_id,
                assumptions=assumptions,
                unknowns=unknowns,
            )
            for task in tasks
        ]
        validation_errors: list[str] = []
        temporary: list[Path] = []
        for destination, content in zip(destinations, contents):
            temporary_path = destination.with_name(destination.name + ".planning-tmp")
            temporary_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(content, encoding="utf-8")
            temporary.append(temporary_path)
            validation_errors.extend(f"{destination.name}: {error}" for error in validate_task(temporary_path))
        if validation_errors:
            for path in temporary:
                path.unlink(missing_ok=True)
            result["errors"] = validation_errors
            result["next_actions"] = ["fix generated contract before rerunning"]
            return result
        published: list[Path] = []
        try:
            for temporary_path, destination in zip(temporary, destinations):
                os.replace(temporary_path, destination)
                published.append(destination)
        except OSError:
            for destination in reversed(published):
                try:
                    destination.unlink(missing_ok=True)
                except OSError:
                    pass
            for temporary_path in temporary:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
            raise
        result.update({"status": "pass", "requirements_sha256": requirements_sha256, "task_ids": task_ids, "artifacts": [path.relative_to(root).as_posix() for path in destinations], "next_actions": ["review and commit generated task sheets"]})
        return result
    except (OSError, ValueError, TypeError, KeyError) as error:
        result["errors"] = [f"{type(error).__name__}: {error}"]
        return result


def planning_to_dispatch(
    root: Path,
    run_id: str,
    project_facts: dict[str, Any],
    requirement_facts: dict[str, Any],
    task_plan: dict[str, Any],
    *,
    task_id: str | None = None,
    branch: str | None = None,
    baseline: str | None = None,
    approval_mode: str | None = None,
    approved: bool = False,
    role: str = "executor",
    auto_freeze: bool = True,
    expected_requirements_sha256: str | None = None,
) -> dict[str, Any]:
    """Run the fail-closed planning-to-dispatch orchestration.

    The function is intentionally an orchestration boundary: it records every
    stage, stops at the first blocked stage, and never starts an executor.  On
    success it writes no planning product: the stage records and the dispatch
    payload live only in the returned value, and only the frozen task sheet is
    persisted.  Failure, interruption and conflict keep the full audit trail
    under ``.pipeline/planning/<run-id>/``.
    """
    from .core import create_worktree_dispatch, git

    root = Path(root).resolve()
    if approval_mode is None:
        approval_mode = _recorded_approval_mode(root, run_id)
    if approval_mode is None:
        approval_mode = _project_approval_mode(root)
    audit = _planning_run_directory(root, run_id)
    result: dict[str, Any] = {
        "schema": 1, "command": "planning.to-dispatch", "status": "blocked",
        "run_id": run_id, "task_id": task_id, "identity": {}, "stages": [],
        "artifacts": [], "errors": [], "blockers": [],
        "next_actions": [], "unverified": ["executor", "reviewer", "executor evidence"],
    }
    records: list[dict[str, Any]] = []

    def flush_stages() -> None:
        audit.mkdir(parents=True, exist_ok=True)
        for index, record in enumerate(records, 1):
            path = audit / f"{index:02d}-{record['name']}.json"
            _write_planning_json(path, record)
            result["artifacts"].append(str(path))

    def stage(name: str, status: str, value: dict[str, Any]) -> bool:
        record = {"name": name, "status": status, "run_id": run_id,
                  "task_id": result.get("task_id"), **value}
        records.append(record)
        result["stages"].append(record)
        if status != "pass":
            result["status"] = status
            result["errors"].extend(value.get("errors", []))
            result["blockers"].extend(value.get("blockers", []))
            result["next_actions"] = value.get("next_actions", ["recover"])
            flush_stages()
            return False
        return True

    if approval_mode not in {"automatic", "manual"}:
        stage("preflight", "blocked", {"errors": ["invalid approval_mode"], "next_actions": ["fix approval policy"]})
        return result
    if expected_requirements_sha256 is None:
        try:
            _directory, _state = _read_planning_state(root, run_id)
            recorded_hash = _state.get("requirements_sha256")
            if isinstance(recorded_hash, str) and recorded_hash:
                expected_requirements_sha256 = recorded_hash
        except (OSError, ValueError):
            pass
    preflight = planning_preflight(root, expected_requirements_sha256=expected_requirements_sha256)
    if not stage("preflight", preflight.get("status", "blocked"), preflight):
        return result
    gate_input = {"schema": 1, "planning_run_id": run_id}
    if isinstance(project_facts, dict):
        gate_input.update({
            field: project_facts.get(field, [])
            for field in ("facts", "assumptions", "unknowns", "conflicts", "non_goals", "decision_blockers")
        })
    else:
        gate_input.update({field: [] for field in ("facts", "assumptions", "unknowns", "conflicts", "non_goals", "decision_blockers")})
    gate = gate_facts_for_planning(gate_input, planning_run_id=run_id)
    if not stage("facts-gate", gate.get("status", "blocked"), gate):
        return result
    generated = generate_task_sheets(
        root,
        run_id,
        project_facts,
        requirement_facts,
        task_plan,
        expected_requirements_sha256=preflight.get("requirements_sha256"),
        assumptions=project_facts.get("assumptions") if isinstance(project_facts, dict) else None,
        unknowns=project_facts.get("unknowns") if isinstance(project_facts, dict) else None,
    )
    if not stage("task-generation", generated.get("status", "blocked"), generated):
        return result
    task_ids = generated.get("task_ids", [])
    selected = task_id or (task_ids[0] if len(task_ids) == 1 else None)
    if not isinstance(selected, str) or selected not in task_ids:
        stage("contract-consistency", "fail", {"errors": ["task_id must select exactly one generated task"], "next_actions": ["select one task_id"]})
        return result
    result["task_id"] = selected
    sheet = root / "docs" / "tasks" / f"{selected}.md"
    consistency = compare_task_plan_contract(task_plan, sheet, root=root, expected_requirements_sha256=preflight.get("requirements_sha256"), expected_run_id=run_id if generated.get("next_actions") != ["reuse existing generated task sheets"] else None)
    if not stage("contract-consistency", consistency.get("status", "fail"), consistency):
        return result
    freeze_errors = validate_task(sheet)
    if freeze_errors:
        stage("freeze", "fail", {"errors": freeze_errors, "next_actions": ["repair contract and retry"]})
        return result
    if auto_freeze:
        rc, status_output = git(root, "status", "--porcelain=v1", "--untracked-files=all", redact_output=False)
        if rc:
            stage("freeze", "blocked", {"errors": ["unable to inspect freeze status"], "next_actions": ["recover"]})
            return result
        changed = [line[3:].strip() for line in status_output.splitlines() if len(line) >= 4]
        if any(item == sheet.relative_to(root).as_posix() for item in changed):
            rc, _ = git(root, "add", sheet.relative_to(root).as_posix(), redact_output=False)
            if rc:
                stage("freeze", "blocked", {"errors": ["unable to stage generated task sheet"], "next_actions": ["recover"]})
                return result
            rc, _ = git(root, "commit", "-m", f"Freeze generated task {selected}", redact_output=False)
            if rc:
                stage("freeze", "blocked", {"errors": ["unable to freeze generated task sheet"], "next_actions": ["inspect retained freeze state"]})
                return result
    if auto_freeze:
        rc, value = git(root, "rev-parse", "HEAD", redact_output=False)
        if rc == 0:
            baseline = value.strip()
    freeze = {"status": "pass", "task_sheet": str(sheet), "commit_required": True}
    if not stage("freeze", "pass", freeze):
        return result
    if approval_mode == "manual" and not approved:
        stage("approval", "blocked", {"errors": ["manual approval required"], "next_actions": ["approve dispatch and retry"]})
        return result
    branch = branch or selected
    if not baseline:
        stage("dispatch-identity", "blocked", {"errors": ["baseline HEAD unavailable"], "next_actions": ["recover identity"]})
        return result
    dispatch_identity = create_worktree_dispatch(root, sheet, selected, branch, baseline, role=role)
    if not stage("dispatch-identity", dispatch_identity.get("status", "blocked"), dispatch_identity):
        return result
    result["identity"] = dispatch_identity.get("identity", {})
    dispatch = {"schema": 1, "task_id": selected, "role": role, "round": 1,
                "root": str(root), "worktree": dispatch_identity["identity"]["worktree"],
                "branch": branch, "evidence_dir": str(root / ".pipeline" / selected),
                "permissions": {"write_workflow": True, "write_product": role == "executor"},
                "output": "dispatch-ready", "run_id": run_id}
    stage("dispatch", "pass", {"dispatch": dispatch, "next_actions": ["start executor separately"]})
    result["dispatch"] = dispatch
    result["status"] = "dispatch-ready"
    result["next_actions"] = ["start executor separately; do not infer executor success"]
    result["artifacts"] = []
    _purge_successful_planning_run(root, run_id)
    return result


def _contains_sensitive(value: Any, key: str | None = None) -> bool:
    if key and SENSITIVE_NAME_RE.search(key):
        return True
    if isinstance(value, dict):
        return any(_contains_sensitive(item, str(name)) for name, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_sensitive(item) for item in value)
    if isinstance(value, str):
        return bool(SENSITIVE_ASSIGNMENT_RE.search(value) or BEARER_RE.search(value))
    return False


def _progress_directory(root: Path, task_id: str) -> Path:
    root = root.resolve()
    pipeline = root / ".pipeline"
    if pipeline.exists() and pipeline.is_symlink():
        raise ValueError("progress directory escapes project root")
    directory = pipeline / task_id
    if directory.exists() and directory.is_symlink():
        raise ValueError("progress directory escapes project root")
    try:
        if not directory.resolve().is_relative_to(root):
            raise ValueError("progress directory escapes project root")
    except (OSError, RuntimeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error) == "progress directory escapes project root":
            raise
        raise ValueError("progress directory escapes project root") from error
    return directory


def append_progress(root: Path, task_id: str, role: str, event: dict[str, Any]) -> Path:
    """Append one role-scoped JSONL event without replacing existing lines."""
    if role not in ROLES or not _safe_task_id(task_id):
        raise ValueError("invalid role or task id")
    if not isinstance(event, dict):
        raise ValueError("progress event must be an object")
    for field in ("schema", "task_id", "role"):
        if field in event and event[field] not in ({"schema": 1, "task_id": task_id, "role": role}[field], None):
            raise ValueError(f"progress event cannot override {field}")
    if _contains_sensitive(event):
        raise ValueError("secrets are not allowed")
    directory = _progress_directory(Path(root), task_id)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{role}-progress.jsonl"
    if path.exists() and path.is_symlink():
        raise ValueError("progress file escapes project root")
    try:
        if not path.resolve().is_relative_to(Path(root).resolve()):
            raise ValueError("progress file escapes project root")
    except (OSError, RuntimeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error) == "progress file escapes project root":
            raise
        raise ValueError("progress file escapes project root") from error
    clean = {"schema": 1, "task_id": task_id, "role": role, **event}
    # Re-assert identity after the merge so a null optional override cannot
    # change the machine-owned fields.
    clean["schema"], clean["task_id"], clean["role"] = 1, task_id, role
    text = json.dumps(clean, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")
    return path


def _read_evidence_block(path: Path) -> dict[str, Any] | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None
    starts = [i for i, line in enumerate(lines) if line.strip() == "```pipeline-evidence"]
    if len(starts) != 1:
        return None
    ends = [i for i in range(starts[0] + 1, len(lines)) if lines[i].strip() == "```"]
    if len(ends) != 1:
        return None
    try:
        value = json.loads("\n".join(lines[starts[0] + 1:ends[0]]))
    except (json.JSONDecodeError, TypeError):
        return None
    return value if isinstance(value, dict) else None


def _validate_finalization_report(path: Path, task_id: str, expected_role: str) -> bool:
    value = _read_evidence_block(path)
    if value is None:
        return False
    required = ("schema", "task_id", "worktree", "branch", "round", "status", "commands", "assertions", "evidence_refs", "unverified")
    if any(field not in value for field in required):
        return False
    return (
        value.get("schema") == 1
        and value.get("task_id") == task_id
        and value.get("role") == expected_role
        and isinstance(value.get("worktree"), str)
        and bool(value.get("worktree"))
        and isinstance(value.get("branch"), str)
        and bool(value.get("branch"))
        and isinstance(value.get("round"), int)
        and not isinstance(value.get("round"), bool)
        and value.get("round", 0) >= 1
        and str(value.get("status", "")).upper() in {"PASS", "READY-TO-MERGE", "MERGED"}
        and isinstance(value.get("commands"), list)
        and bool(value.get("commands"))
        and isinstance(value.get("assertions"), list)
        and bool(value.get("assertions"))
        and all(isinstance(item, str) and item.strip() for item in value["assertions"])
        and isinstance(value.get("evidence_refs"), list)
        and bool(value.get("evidence_refs"))
        and isinstance(value.get("unverified"), list)
    )


def _validate_finalization_acceptance(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for item in value:
        if not isinstance(item, dict):
            return False
        if not isinstance(item.get("id"), str) or not item["id"].strip():
            return False
        if str(item.get("status", "")).lower() != "pass":
            return False
        if isinstance(item.get("exit_code"), bool) or item.get("exit_code") != 0:
            return False
        if not isinstance(item.get("evidence_refs"), list) or not item["evidence_refs"]:
            return False
    return True


def _validate_result(path: Path, task_id: str, expected_role: str) -> bool:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    if not isinstance(value, dict):
        return False
    role = value.get("role")
    role_ok = role in {expected_role, "main-final"} if expected_role == "main" else role == expected_role
    return (
        value.get("schema") == 1
        and value.get("task_id") == task_id
        and role_ok
        and str(value.get("status", "")).lower() == "pass"
        and isinstance(value.get("acceptance"), list)
        and isinstance(value.get("unverified"), list)
    )


def _evidence_project_root(directory: Path) -> Path:
    resolved = directory.resolve()
    parts = list(resolved.parts)
    if ".pipeline" in parts:
        index = len(parts) - 1 - list(reversed(parts)).index(".pipeline")
        return Path(*parts[:index]) if index else Path(resolved.anchor)
    return resolved.parent


def _resolve_evidence_reference(directory: Path, reference: str) -> Path | None:
    text = reference.replace("\\", "/")
    if (
        not text
        or "\x00" in text
        or text.startswith("/")
        or WINDOWS_ABSOLUTE_RE.match(text)
        or ".." in PurePosixPath(text).parts
    ):
        return None
    root = _evidence_project_root(directory)
    candidate = root / text if text.startswith((".pipeline/", ".workflow/")) else directory / text
    try:
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root.resolve()):
            return None
        return resolved
    except (OSError, RuntimeError, ValueError):
        return None


def _validate_retained_references(directory: Path, references: Iterable[str], retained: set[str]) -> list[str]:
    errors: list[str] = []
    directory_resolved = directory.resolve()
    for reference in references:
        candidate = _resolve_evidence_reference(directory, reference)
        if candidate is None or not candidate.is_file():
            errors.append(reference)
            continue
        try:
            relative = candidate.relative_to(directory_resolved).as_posix()
        except ValueError:
            errors.append(reference)
            continue
        if relative not in retained:
            errors.append(reference)
    return errors


def _extract_evidence_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"evidence_ref", "evidence_refs", "artifact", "artifacts"}:
                if isinstance(item, str):
                    refs.append(item)
                elif isinstance(item, list):
                    refs.extend(x for x in item if isinstance(x, str))
            else:
                refs.extend(_extract_evidence_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.extend(_extract_evidence_refs(item))
    return refs


def _normalise_evidence_reference(directory: Path, reference: str) -> str | None:
    text = reference.replace("\\", "/")
    if not text or "\x00" in text or text.startswith("/") or WINDOWS_ABSOLUTE_RE.match(text):
        return None
    if ".." in PurePosixPath(text).parts:
        return None
    # References are commonly either task-directory-relative or project
    # relative (.pipeline/<task>/...).
    if text.startswith(".pipeline/") or text.startswith(".workflow/"):
        return text
    return f"{directory.name}/{text}"


def _evidence_directory_identity(directory: Path, task_id: str) -> bool:
    if not _safe_task_id(task_id) or not directory.is_dir() or directory.is_symlink():
        return False
    parts = directory.resolve().parts
    if ".pipeline" in parts:
        index = len(parts) - 1 - list(reversed(parts)).index(".pipeline")
        return index + 1 < len(parts) and parts[index + 1] == task_id
    # Keep support for isolated temporary evidence directories used by callers
    # and old reports; such paths are still bounded by their own directory.
    return True


def finalize_evidence(directory: Path, task_id: str, success: bool) -> dict[str, Any]:
    """Finalize only an approved evidence set, preserving failure现场."""
    directory = Path(directory)
    required = [
        "executor-report.md", "executor-result.json",
        "review-report.md", "reviewer-result.json",
        "final-check.md", "final-result.json",
    ]
    retained = list(RETAINED_EVIDENCE_NAMES)
    if not _evidence_directory_identity(directory, task_id):
        return {"status": "blocked", "missing": ["evidence directory identity"], "finalization": None}
    marker = directory / "finalization.json"
    if marker.is_file():
        try:
            existing = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return {"status": "blocked", "missing": ["valid finalization.json"], "finalization": None}
        if existing.get("task_id") == task_id and existing.get("status") == "finalized":
            return {"status": "finalized", "missing": [], "finalization": str(marker)}
        return {"status": "blocked", "missing": ["finalization identity"], "finalization": None}

    missing = [name for name in required if not (directory / name).is_file()]
    if not success:
        return {"status": "blocked", "missing": missing, "finalization": None}
    if missing:
        return {"status": "blocked", "missing": missing, "finalization": None}

    valid_roles = {
        "executor-report.md": "executor",
        "review-report.md": "reviewer",
        "final-check.md": "main-final",
    }
    invalid: list[str] = []
    for name, role in valid_roles.items():
        if not _validate_finalization_report(directory / name, task_id, role):
            invalid.append(f"invalid {name}")
    for name, role in (
        ("executor-result.json", "executor"),
        ("reviewer-result.json", "reviewer"),
        ("final-result.json", "main"),
    ):
        if not _validate_result(directory / name, task_id, role):
            invalid.append(f"invalid {name}")
    try:
        final_result = json.loads((directory / "final-result.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        final_result = {}
    if not isinstance(final_result, dict) or final_result.get("decision") != "READY_FOR_EVIDENCE_FINALIZATION":
        invalid.append("final-result.json approval")
    if invalid:
        return {"status": "blocked", "missing": invalid, "finalization": None}

    # Do not delete an artifact still referenced by any retained report/result.
    refs: list[str] = []
    for name in required:
        if name.endswith(".md"):
            value = _read_evidence_block(directory / name)
        else:
            try:
                value = json.loads((directory / name).read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                value = None
        refs.extend(_extract_evidence_refs(value))
    refs = [reference for reference in refs if not reference.startswith(".pipeline/") or Path(reference).name not in {"blocker-facts.json"}]
    dangling = _validate_retained_references(directory, refs, set(retained))
    if dangling:
        return {
            "status": "blocked",
            "missing": [f"referenced process evidence would be deleted or is unsafe: {item}" for item in dangling],
            "finalization": None,
        }

    value = {
        "schema": 1,
        "task_id": task_id,
        "status": "finalized",
        "retained": retained,
        "approved_by": "main",
    }
    staging = directory / ".finalization-staging"
    backup = staging / ".backup"
    moved: list[tuple[Path, Path]] = []
    try:
        if staging.exists():
            raise OSError("stale finalization staging directory")
        staging.mkdir()
        retained_set = set(retained)
        for path in sorted(directory.rglob("*"), key=lambda item: len(item.parts)):
            if path == staging or staging in path.parents:
                continue
            relative = path.relative_to(directory).as_posix()
            if relative in retained_set:
                continue
            staged = staging / path.relative_to(directory)
            if path.is_file() or path.is_symlink():
                staged.parent.mkdir(parents=True, exist_ok=True)
                os.replace(path, staged)
                moved.append((path, staged))
        for original, staged in moved:
            preserved = backup / original.relative_to(directory)
            preserved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(staged, preserved, follow_symlinks=False)
        for _original, staged in reversed(moved):
            if staged.exists():
                staged.unlink()
        shutil.rmtree(staging)
        temporary = marker.with_suffix(".tmp")
        temporary.write_text(json.dumps(value, ensure_ascii=True, indent=2), encoding="utf-8")
        os.replace(temporary, marker)
    except (OSError, ValueError, RuntimeError) as error:
        temporary = marker.with_suffix(".tmp")
        if temporary.exists():
            temporary.unlink()
        for original, staged in moved:
            preserved = backup / original.relative_to(directory)
            if preserved.exists():
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(preserved, original, follow_symlinks=False)
            elif staged.exists():
                original.parent.mkdir(parents=True, exist_ok=True)
                os.replace(staged, original)
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        return {"status": "blocked", "missing": [f"cleanup failed: {type(error).__name__}"], "finalization": None}
    return {"status": "finalized", "missing": [], "finalization": str(marker)}
