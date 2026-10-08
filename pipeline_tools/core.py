"""Mechanical workflow checks, bounded command execution, and local metrics."""

from __future__ import annotations

import fnmatch
import json
import os
import re
import signal
import subprocess
import tempfile
import time
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from .layout import (
    active_pipeline_dir,
    canonical_evidence_dir,
    evidence_root,
    is_metrics_path,
    metrics_dirs,
    temporary_log_path,
)
from .contract import CHAIN_NAMES, load_contract, validate_task

PASS, FAIL, CONFIG, BLOCKED, DRIFT = 0, 1, 2, 3, 4
REPORT_NAMES = ("executor-report.md", "review-report.md", "final-check.md")
MACHINE_RESULT_NAMES = ("executor-result.json", "reviewer-result.json", "final-result.json")
# The only evidence files a successfully finalized task directory keeps. Both
# the history gate (this module) and evidence finalization (planning) read this
# one source so the retained set can never drift apart.
RETAINED_EVIDENCE_NAMES = REPORT_NAMES + MACHINE_RESULT_NAMES + ("finalization.json",)
CONFIDENCES = {"observed", "derived", "reported"}
METRIC_RESULTS = {"pass", "passed", "fail", "failed", "blocked", "flaky", "unknown"}
BLOCKER_CLASSES = {"product", "environment", "permission", "evidence", "dependency", "workflow", None}
# One shared read-side normalization table.  Markdown evidence blocks are written
# in upper case and machine result JSON in lower case, so neither spelling can be
# made canonical without rewriting history.  Both readers instead normalize what
# they read onto the canonical spelling of their own vocabulary.
REPORT_STATUSES = ("PASS", "FAIL", "BLOCKED", "FLAKY", "EXPLORATORY_ONLY", "READY-TO-MERGE", "MERGED")
PRE_MERGE_REPORT_STATUSES = ("PASS", "READY-TO-MERGE")
POST_MERGE_REPORT_STATUSES = ("PASS", "READY-TO-MERGE", "MERGED")
# Evidence identity is phase aware.  Before the merge the evidence is bound to the
# commits it observed, so head, branch and worktree must match the current Git
# identity.  After the merge that binding cannot hold: merging always introduces
# product-path commits into the current head, so identity there is the task id
# plus the task sheet revision, and the commit references stay recorded facts.
EVIDENCE_PHASES = ("active", "finalized")
RESULT_STATUSES = ("pass", "fail", "blocked", "flaky")
ACCEPTANCE_STATUSES = ("pass", "fail", "blocked", "flaky", "unverified")
# The only status spelling that ever shipped but belongs to neither vocabulary.
LEGACY_STATUS_ALIASES = {"pass_with_conditions": "pass"}
RESULT_ROLE_ALIASES = {"main": "main-final", "final": "main-final"}
_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _safe_task_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(_TASK_ID_RE.fullmatch(value)) and value not in {".", ".."}


def _has_reparse_or_symlink(path: Path) -> bool:
    current = path
    while True:
        try:
            if current.is_symlink():
                return True
            stat_result = current.lstat()
            attributes = getattr(stat_result, "st_file_attributes", 0)
            if attributes & 0x400:
                return True
        except FileNotFoundError:
            pass
        except OSError:
            return True
        if current.parent == current:
            return False
        current = current.parent


def _canonical_workflow_directory(root: Path, workflow_directory: Path) -> tuple[Path | None, str | None]:
    root = Path(root)
    if not _safe_task_identifier(workflow_directory.name):
        return None, "workflow directory task identifier is unsafe"
    canonical = root / ".pipeline" / workflow_directory.name
    try:
        if Path(workflow_directory).is_absolute():
            supplied = Path(workflow_directory)
        else:
            supplied = root / workflow_directory
        if supplied.absolute() != canonical.absolute():
            return None, "workflow directory must exactly match canonical .pipeline/<task-id>"
    except OSError:
        return None, "workflow directory path is invalid"
    if _has_reparse_or_symlink(root) or _has_reparse_or_symlink(root / ".pipeline") or _has_reparse_or_symlink(canonical):
        return None, "workflow directory or its parents must not be a symlink or reparse point"
    return canonical, None

_SECRET_RE = re.compile(
    r"(?i)\b(password|passwd|token|secret|authorization|api[_-]?key|cvc)\b"
    r"(\s*[=:]\s*)[^\s,;]+"
)
_BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(?:[A-Za-z]:[\\/]|/(?:Users|home|tmp|var|opt|private|etc|root)(?:/|$)|/)[^\r\n\t\s,;]*")


def _status_key(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    key = value.strip().lower().replace("-", "_")
    return key or None


def normalize_status(value: Any, vocabulary: tuple[str, ...]) -> str | None:
    """Return ``value`` rewritten as the matching entry of ``vocabulary``.

    Matching ignores case and treats ``-`` and ``_`` as the same separator, so a
    status written in the other side's case is still read.  The single legacy
    spelling ``pass_with_conditions`` folds onto ``pass``.  A value that matches
    no entry -- including after aliasing -- returns ``None`` and stays invalid.
    """
    key = _status_key(value)
    if key is None:
        return None
    key = LEGACY_STATUS_ALIASES.get(key, key)
    for candidate in vocabulary:
        if _status_key(candidate) == key:
            return candidate
    return None


def resolve_result_role(role: Any) -> Any:
    """Map a caller-facing role name onto the role a machine result records."""
    if not isinstance(role, str):
        return role
    return RESULT_ROLE_ALIASES.get(role.strip().lower(), role)


def redact(value: Any) -> str:
    """Redact secrets and common local identity paths before output is persisted."""
    text = str(value or "")
    text = _SECRET_RE.sub(r"\1\2<redacted>", text)
    text = _BEARER_RE.sub("Bearer <redacted>", text)
    return _PATH_RE.sub("<path>", text)


def git(
    root: Path,
    *args: str,
    timeout: float = 20,
    redact_output: bool = True,
) -> tuple[int, str]:
    """Run a read-only Git command with a bounded wait."""
    if not root.is_dir():
        return CONFIG, "working directory does not exist"
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        return CONFIG, "git executable not found"
    except subprocess.TimeoutExpired:
        return CONFIG, "git command timed out"
    # Do NOT strip: porcelain output is column-sensitive (a leading space is
    # part of the XY status code for the first line).
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, redact(output) if redact_output else output


def _write_log(path: Path, content: str) -> str | None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        return f"unable to write log: {type(exc).__name__}"
    return None


def _atomic_write_text(path: Path, content: str) -> None:
    """Replace a text file in one step so a failure leaves the old bytes intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
    else:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except (OSError, ProcessLookupError):
            pass
    try:
        process.kill()
    except (OSError, ProcessLookupError):
        pass


def run_command(command: list[str], cwd: Path, log: Path | None = None, timeout: float = 180) -> dict[str, Any]:
    """Run a command without a shell and write raw output to a transient log by default."""
    command = list(command)
    if command and command[0] == "--":
        command = command[1:]
    if not command or timeout <= 0:
        raise ValueError("command and positive timeout required")
    if not cwd.is_dir():
        raise ValueError("working directory does not exist")

    if log is None:
        log_path = temporary_log_path(root=cwd)
    else:
        log_path = log if log.is_absolute() else cwd / log
        if log_path.is_symlink():
            raise ValueError("explicit log path must not be a symlink")
        if log_path.exists() and log_path.is_symlink():
            raise ValueError("explicit log path must not be a symlink")
    started = time.monotonic()
    kwargs: dict[str, Any] = {
        "cwd": cwd,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["start_new_session"] = True

    try:
        process = subprocess.Popen(command, **kwargs)
    except (OSError, ValueError) as exc:
        content = redact(f"{type(exc).__name__}: {exc}")
        log_error = _write_log(log_path, content)
        return {
            "status_code": CONFIG,
            "exit_code": None,
            "timed_out": False,
            "duration_s": round(time.monotonic() - started, 3),
            "log": str(log_path),
            "output": content,
            "error": log_error or "command could not start",
        }

    timed_out = False
    try:
        output, _ = process.communicate(timeout=timeout)
        exit_code = process.returncode
        status_code = PASS if exit_code == 0 else FAIL
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_process_tree(process)
        try:
            output, _ = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            output = "process did not terminate during cleanup"
            _terminate_process_tree(process)
        # The public exit_code is the workflow result for a timeout.
        exit_code = BLOCKED
        status_code = BLOCKED

    content = redact(output or "")
    log_error = _write_log(log_path, content)
    if log_error:
        status_code = CONFIG
    return {
        "status_code": status_code,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration_s": round(time.monotonic() - started, 3),
        "log": str(log_path),
        "output": content,
        "error": log_error,
    }


def _normalize_path(value: str) -> str:
    value = value.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.rstrip("/") if value != "/" else value


def _matches(path: str, pattern: str, root: Path | None = None) -> bool:
    path = _normalize_path(path)
    pattern = _normalize_path(pattern)
    if fnmatch.fnmatchcase(path, pattern):
        return True
    if root is not None and (
        Path(pattern).is_absolute() or bool(re.match(r"^[A-Za-z]:/", pattern))
    ):
        absolute_path = _normalize_path(str((root / path).resolve()))
        if fnmatch.fnmatchcase(absolute_path, pattern):
            return True
    if pattern.endswith("/**"):
        base = pattern[:-3].rstrip("/")
        return path == base or path.startswith(base + "/")
    return False


def _status_paths(output: str) -> list[str]:
    paths: set[str] = set()
    for line in output.splitlines():
        if len(line) < 4:
            continue
        # Porcelain codes are exactly two columns. git() must preserve the
        # output's leading space so the path always begins at column three.
        value = line[3:]
        if " -> " in value:
            value = value.rsplit(" -> ", 1)[1]
        value = value.strip().strip('"').replace("\\", "/")
        if value:
            paths.add(value)
    return sorted(paths)


def commit_history_check(
    root: Path,
    evidence_root: str,
    *,
    metrics_root: str = ".pipeline/metrics",
    since: str | None = None,
) -> list[str]:
    """Reject commits that touched active evidence, except metrics.

    Additions and modifications violate when the basename is outside the
    retained set; deletions only violate when they remove a retained file, so
    cleaning up scratch evidence is not itself drift. ``since`` bounds the scan
    to ``<since>..HEAD``; when it is omitted the whole reachable history is
    scanned, exactly as before.
    """
    evidence_root = _normalize_path(evidence_root)
    metrics_root = _normalize_path(metrics_root)
    revision_range = f"{since}..HEAD" if since else "--all"
    rc, output = git(root, "log", revision_range, "--format=%H", "--name-status", redact_output=False)
    if rc:
        return [output or "unable to inspect commit history"]
    violations: list[str] = []
    current_commit = ""
    for line in output.splitlines():
        if re.fullmatch(r"[0-9a-fA-F]{40}", line.strip()):
            current_commit = line.strip()
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, paths = parts[0], parts[1:]
        deleting = status.startswith("D")
        for path in paths:
            normalized = _normalize_path(path)
            in_evidence = normalized == evidence_root or normalized.startswith(evidence_root.rstrip("/") + "/")
            in_metrics = normalized == metrics_root or normalized.startswith(metrics_root.rstrip("/") + "/")
            if is_progress_log_path(normalized):
                violations.append(f"{current_commit}: {status} {normalized} (progress log must not enter Git)")
            elif in_evidence and not in_metrics:
                # Removing a retained file is drift; removing scratch evidence is
                # the cleanup the retention contract asks for.
                retained = Path(normalized).name in RETAINED_EVIDENCE_NAMES
                if retained == deleting:
                    violations.append(f"{current_commit}: {status} {normalized}")
    return violations


def scope_check(root: Path, allowed: list[str], forbidden: list[str]) -> list[str]:
    """Return changed paths outside the allow-list or inside the deny-list."""
    rc, output = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if rc:
        return [output or "not a git repository"]
    allowed = allowed or []
    forbidden = forbidden or []
    bad = []
    for path in _status_paths(output):
        # Automatically generated metrics are workflow metadata and may be
        # tracked by the host project. They must not turn every frozen task
        # scope check into a product-scope failure.
        normalized = _normalize_path(path)
        if normalized == ".workflow/metrics" or normalized.startswith(".workflow/metrics/"):
            active_pipeline_dir(root)
            normalized = normalized.replace(".workflow/", ".pipeline/", 1)
        forbidden_match = any(_matches(path, pattern, root) for pattern in forbidden)
        allowed_match = any(_matches(path, pattern, root) for pattern in allowed)
        if (is_metrics_path(normalized) or is_progress_log_path(normalized)) and not forbidden_match:
            continue
        if forbidden_match or not allowed_match:
            bad.append(path)
    return bad


def _validate_evidence_ref(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace(chr(92), "/")
    return not (
        Path(normalized).is_absolute()
        or bool(re.match(r"^[A-Za-z]:/", normalized))
        or normalized.startswith("/")
        or ".." in normalized.split("/")
    )


def _evidence_root(directory: Path) -> Path:
    return evidence_root(directory)


def _canonical_evidence_dir(directory: Path) -> Path:
    supplied = Path(directory)
    candidate = supplied if supplied.is_absolute() else Path.cwd() / supplied
    candidate = candidate.absolute()
    if candidate.parent.name != ".pipeline":
        raise ValueError("evidence directory must exactly match canonical .pipeline/<task-id>")
    task_id = candidate.name
    if not _safe_task_identifier(task_id):
        raise ValueError("evidence task identifier is unsafe")
    root = candidate.parent.parent
    canonical = root / ".pipeline" / task_id
    if candidate != canonical:
        raise ValueError("evidence directory must exactly match canonical .pipeline/<task-id>")
    if _has_reparse_or_symlink(root) or _has_reparse_or_symlink(root / ".pipeline") or _has_reparse_or_symlink(candidate):
        raise ValueError("evidence directory or its parents must not be a symlink or reparse point")
    return canonical


def _evidence_file_exists(directory: Path, reference: Any) -> bool:
    if not _validate_evidence_ref(reference):
        return False
    normalized = str(reference).replace(chr(92), "/")
    evidence_directory = directory.resolve()
    project_root = _evidence_root(directory).resolve()
    base = project_root if normalized == ".pipeline" or normalized.startswith(".pipeline/") else evidence_directory
    candidate = (base / normalized).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return False
    return candidate.is_file()


def _read_machine_evidence(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, ["unreadable"]

    lines = text.splitlines()
    starts = [
        index
        for index, line in enumerate(lines)
        if line.strip() == "```pipeline-evidence"
    ]
    if len(starts) != 1:
        return None, ["missing or duplicate pipeline-evidence block"]
    start = starts[0]
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].strip() == "```"),
        None,
    )
    if end is None:
        return None, ["pipeline-evidence block is not closed"]
    body = "\n".join(lines[start + 1 : end])
    try:
        value = json.loads(body)
    except json.JSONDecodeError:
        return None, ["pipeline-evidence JSON is invalid"]
    if not isinstance(value, dict):
        return None, ["pipeline-evidence must be an object"]
    return value, []


def evidence_verify(
    directory: Path,
    task_id: str,
    branch: str | None = None,
    phase: str = "active",
) -> list[str]:
    """Verify machine-readable report identity and minimum evidence fields.

    ``phase`` selects the identity criterion set.  ``active`` (pre-merge) binds a
    report to the commit it observed: its ``head`` must equal the current head or
    only be advanced by its own evidence, and its ``branch``/``worktree`` must
    equal the current Git identity.  ``finalized`` (post-merge) identifies the
    evidence by the task id and the task sheet revision alone, because merging
    always adds product-path commits to the current head; ``head``, ``branch``,
    ``worktree`` and ``observed_at_commit`` stay required, format-checked records.
    """
    if phase not in EVIDENCE_PHASES:
        raise ValueError(f"evidence phase must be one of {EVIDENCE_PHASES}")
    directory = _canonical_evidence_dir(directory)
    commit_bound = phase == "active"
    errors: list[str] = []
    reports: dict[str, dict[str, Any]] = {}
    root = _evidence_root(directory)
    current_identity = git_identity(root)
    current_revision = None if commit_bound else task_sheet_revision(root, task_id)[0]
    if not commit_bound and directory.name != task_id:
        errors.append("evidence directory does not match the verified task id")
    expected_roles = {
        "executor-report.md": "executor",
        "review-report.md": "reviewer",
        "final-check.md": "main-final",
    }
    required = (
        "schema",
        "task_id",
        "worktree",
        "branch",
        "role",
        "round",
        "status",
        "commands",
        "assertions",
        "evidence_refs",
        "unverified",
    )

    for name in REPORT_NAMES:
        path = directory / name
        if not path.is_file():
            errors.append(f"missing {name}")
            continue
        if not path.read_text(encoding="utf-8", errors="replace").strip():
            errors.append(f"{name} is empty")
            continue
        value, parse_errors = _read_machine_evidence(path)
        if parse_errors:
            errors.extend(f"{name}: {item}" for item in parse_errors)
            continue
        assert value is not None
        reports[name] = value

        for field in required:
            if field not in value:
                errors.append(f"{name} missing field: {field}")
        schema = value.get("schema")
        if schema not in {1, 2}:
            errors.append(f"{name} schema must be 1 or 2")
        if schema == 2:
            for field in ("head", "generated_at"):
                if not isinstance(value.get(field), str) or not value.get(field).strip():
                    errors.append(f"{name} {field} must be a non-empty string")
            if isinstance(value.get("head"), str) and not re.fullmatch(r"[0-9a-fA-F]{40}", value["head"]):
                errors.append(f"{name} head is not a valid commit")
            if isinstance(value.get("generated_at"), str):
                try:
                    datetime.fromisoformat(value["generated_at"].replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"{name} generated_at is not ISO-8601")
        if value.get("task_id") != task_id:
            errors.append(f"{name} task identity mismatch")
        if value.get("schema") == 2:
            # Pre-merge the recorded commit, branch and worktree bind the report to
            # the current Git identity; post-merge they are recorded facts and the
            # identity is the task id plus the task sheet revision.
            if commit_bound:
                # The report names the commit it judged. Committing the report itself
                # (task evidence only) moves HEAD, so accept an evidence-only advance
                # instead of letting the record invalidate itself; anything else keeps
                # the strict identity rule.
                reported_head = value.get("head")
                if reported_head != current_identity.get("head") and not head_advanced_by_evidence_only(
                    root, reported_head, current_identity.get("head"), directory
                ):
                    errors.append(f"{name} head does not match current Git identity")
                if value.get("branch") != (branch or current_identity.get("branch")):
                    errors.append(f"{name} branch does not match current Git identity")
                try:
                    report_worktree = Path(value.get("worktree", "")).resolve()
                except (OSError, ValueError):
                    report_worktree = None
                current_worktree = current_identity.get("worktree")
                if not current_worktree or report_worktree != Path(current_worktree):
                    errors.append(f"{name} worktree does not match current Git identity")
            else:
                declared_revision = value.get("sheet_revision")
                if isinstance(declared_revision, bool) or not isinstance(declared_revision, int):
                    errors.append(f"{name} sheet_revision must be a positive integer")
                elif declared_revision != current_revision:
                    errors.append(
                        f"{name} was produced against task sheet revision {declared_revision} "
                        f"but the current revision is {current_revision}"
                    )
                if not isinstance(value.get("branch"), str) or not value["branch"].strip():
                    errors.append(f"{name} branch must be a non-empty string")
                if (
                    not isinstance(value.get("observed_at_commit"), str)
                    or not value["observed_at_commit"].strip()
                ):
                    errors.append(f"{name} observed_at_commit must be a non-empty string")
        if commit_bound and branch and value.get("branch") != branch:
            errors.append(f"{name} branch mismatch")
        if value.get("role") != expected_roles[name]:
            errors.append(f"{name} role mismatch")
        if not isinstance(value.get("worktree"), str) or not value.get("worktree"):
            errors.append(f"{name} worktree must be non-empty")
        if isinstance(value.get("round"), bool) or not isinstance(value.get("round"), int) or value.get("round", 0) < 1:
            errors.append(f"{name} round must be a positive integer")
        if normalize_status(value.get("status"), REPORT_STATUSES) is None:
            errors.append(f"{name} status is invalid")

        commands = value.get("commands")
        if not isinstance(commands, list) or not commands:
            errors.append(f"{name} commands must be non-empty")
        else:
            for index, command in enumerate(commands, start=1):
                if not isinstance(command, dict):
                    errors.append(f"{name} command {index} must be an object")
                    continue
                if not isinstance(command.get("command"), str) or not command.get("command"):
                    errors.append(f"{name} command {index} has no command")
                expected = command.get("expected_exit_code")
                if expected is not None and (
                    isinstance(expected, bool) or not isinstance(expected, int)
                ):
                    errors.append(f"{name} command {index} expected_exit_code must be an integer")
                if isinstance(command.get("exit_code"), bool) or not isinstance(command.get("exit_code"), int):
                    errors.append(f"{name} command {index} has no numeric exit_code")
                elif not _evidence_file_exists(directory, command.get("evidence_ref")):
                    errors.append(f"{name} command {index} evidence_ref is missing or not relative")
                cwd = command.get("cwd")
                if cwd is not None and (not isinstance(cwd, str) or not cwd.strip()):
                    errors.append(f"{name} command {index} cwd must be a non-empty string")

        assertions = value.get("assertions")
        if not isinstance(assertions, list) or not assertions or any(
            not isinstance(item, str) or not item.strip() for item in assertions
        ):
            errors.append(f"{name} assertions must be non-empty strings")
        refs = value.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{name} evidence_refs must be non-empty")
        else:
            for reference in refs:
                if not _evidence_file_exists(directory, reference):
                    errors.append(f"{name} evidence_ref is missing or not relative")
        if not isinstance(value.get("unverified"), list):
            errors.append(f"{name} unverified must be an array")

    return errors


def is_progress_log_path(path: str) -> bool:
    """Return whether a normalized project-relative path is a role progress log."""
    normalized = _normalize_path(path)
    parts = normalized.split("/")
    return (
        len(parts) == 3
        and parts[0] in {".pipeline", ".workflow"}
        and bool(parts[1])
        and parts[2].endswith("-progress.jsonl")
    )


def _metrics_dir(root: Path) -> Path:
    return active_pipeline_dir(root) / "metrics"


def _metric_bool(value: Any, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def evidence_readiness(directory: Path, task_id: str) -> dict[str, Any]:
    """Classify evidence preparation before formal verification or merge gates."""
    directory = _canonical_evidence_dir(directory)
    reports = list(REPORT_NAMES)
    results = list(MACHINE_RESULT_NAMES)
    missing_reports = [name for name in reports if not (directory / name).is_file()]
    missing_results = [name for name in results if not (directory / name).is_file()]
    if missing_reports:
        status = "not_ready"
        layer = "reports"
    elif missing_results:
        status = "not_ready"
        layer = "machine_results"
    else:
        status = "ready"
        layer = "complete"
    missing = missing_reports + missing_results
    return {
        "schema": 1,
        "command": "evidence.readiness",
        "task_id": task_id,
        "status": status,
        "layer": layer,
        "missing": missing,
        "missing_reports": missing_reports,
        "missing_machine_results": missing_results,
        "errors": [],
        "blockers": [] if not missing else [{"class": "evidence", "reason": f"missing {layer} artifacts"}],
        "observed": [{"fact": "required_reports", "value": reports}, {"fact": "required_machine_results", "value": results}],
        "next_actions": [] if not missing else ["complete_evidence_set"],
        "unverified": [] if not missing else ["formal evidence verification"],
    }


def _safe_identifier(value: Any) -> str:
    text = str(value or "")
    if (
        re.search(r"(?i)(secret|token|password|api[_-]?key|passwd|authorization|bearer|cvc)", text)
        or _BEARER_RE.search(text)
        or _PATH_RE.search(text)
    ):
        return "unknown"
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", text)
    return cleaned or "unknown"


def _relative_reference(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).replace(chr(92), "/")
    if not text or Path(text).is_absolute() or text.startswith(("/", "../")):
        return None
    if ".." in text.split("/"):
        return None
    if (
        any(re.search(r"(?i)(secret|token|password|api[_-]?key|passwd|authorization|cvc)", part) for part in text.split("/"))
        or _BEARER_RE.search(text)
    ):
        return None
    return text


def metric_event(root: Path, event: dict[str, Any]) -> Path:
    """Write one allow-listed, local, atomic metric event."""
    confidence = event.get("confidence")
    if confidence not in CONFIDENCES:
        raise ValueError("invalid confidence")
    name = event.get("event")
    if not isinstance(name, str) or not name.strip() or len(name) > 80:
        raise ValueError("event must be a non-empty short string")
    result = event.get("result")
    if result is not None and result not in METRIC_RESULTS and result not in (0, 1):
        raise ValueError("invalid result")
    token_count = event.get("token_count")
    if token_count is not None and (
        isinstance(token_count, bool) or not isinstance(token_count, int) or token_count < 0
    ):
        raise ValueError("token_count must be a non-negative integer or null")
    evidence_ref = event.get("evidence_ref")
    if evidence_ref is not None and not _validate_evidence_ref(evidence_ref):
        raise ValueError("evidence_ref must be a project-relative path or null")
    evidence_root = event.get("evidence_root")
    if evidence_root is not None and not _validate_evidence_ref(evidence_root):
        raise ValueError("evidence_root must be a project-relative path or null")
    blocker_class = event.get("blocker_class")
    if blocker_class not in BLOCKER_CLASSES:
        raise ValueError("invalid blocker_class")

    clean: dict[str, Any] = {
        "schema": 1,
        "event_id": uuid.uuid4().hex,
        "recorded_at": time.time_ns(),
        "event": _safe_identifier(name),
        "confidence": confidence,
        "task_id": _safe_identifier(event.get("task_id", "unknown")),
        "result": result if result is not None else "unknown",
        "duration_s": event.get("duration_s"),
        "timed_out": event.get("timed_out"),
        "token_count": token_count,
        "reason": _safe_identifier(event["reason"]) if event.get("reason") else None,
        "attempt": event.get("attempt", 0),
        "evidence_ref": _relative_reference(evidence_ref),
        "evidence_root": _relative_reference(evidence_root),
        "blocker_class": blocker_class,
        "source": _safe_identifier(event["source"]) if event.get("source") else None,
        "run_id": _safe_identifier(event["run_id"]) if event.get("run_id") else None,
        "phase": _safe_identifier(event["phase"]) if event.get("phase") else None,
        "role": _safe_identifier(event["role"]) if event.get("role") else None,
        "head": _safe_identifier(event["head"]) if event.get("head") else None,
        "branch": _safe_identifier(event["branch"]) if event.get("branch") else None,
        "terminal": event.get("terminal"),
        "supersedes": _safe_identifier(event["supersedes"]) if event.get("supersedes") else None,
    }
    if clean["duration_s"] is not None and (
        isinstance(clean["duration_s"], bool)
        or not isinstance(clean["duration_s"], (int, float))
        or clean["duration_s"] < 0
    ):
        raise ValueError("duration_s must be non-negative or null")
    if not isinstance(clean["timed_out"], (bool, type(None))):
        raise ValueError("timed_out must be boolean or null")
    if not isinstance(clean["terminal"], (bool, type(None))):
        raise ValueError("terminal must be boolean or null")
    if isinstance(clean["attempt"], bool) or not isinstance(clean["attempt"], int) or clean["attempt"] < 0:
        raise ValueError("attempt must be a non-negative integer")

    directory = _metrics_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{clean['recorded_at']}-{clean['event_id']}.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(clean, ensure_ascii=True, sort_keys=True), encoding="utf-8")
    os.replace(temporary, target)
    return target


def _load_metric_events(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    invalid: list[str] = []
    seen_event_ids: set[str] = set()
    for directory in metrics_dirs(root):
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(value, dict) or value.get("schema") != 1:
                    raise ValueError("invalid schema")
                if value.get("confidence") not in CONFIDENCES:
                    raise ValueError("invalid confidence")
                event_id = value.get("event_id")
                if isinstance(event_id, str) and event_id in seen_event_ids:
                    continue
                if isinstance(event_id, str):
                    seen_event_ids.add(event_id)
                value.setdefault("terminal", None)
                value.setdefault("run_id", None)
                value.setdefault("phase", None)
                value.setdefault("role", None)
                value.setdefault("head", None)
                value.setdefault("branch", None)
                value.setdefault("evidence_root", None)
                rows.append(value)
            except (OSError, json.JSONDecodeError, ValueError):
                invalid.append(path.name)
    return rows, invalid


def aggregate(
    root: Path,
    *,
    task_id: str | None = None,
    run_id: str | None = None,
    terminal_only: bool = False,
    include_derived: bool = True,
) -> dict[str, Any]:
    rows, invalid = _load_metric_events(root)
    if invalid:
        raise ValueError(f"invalid metric event files: {len(invalid)}")
    filtered = [row for row in rows if task_id is None or row.get("task_id") == task_id]
    filtered = [row for row in filtered if run_id is None or row.get("run_id") == run_id]
    filtered = [row for row in filtered if not terminal_only or _metric_bool(row.get("terminal"))]
    core = [row for row in filtered if row.get("confidence") == "observed" or (include_derived and row.get("confidence") == "derived")]
    reported = [row for row in filtered if row.get("confidence") == "reported"]
    passed = sum(row.get("result") in {"pass", "passed", 0} for row in core)
    failed = sum(row.get("result") in {"fail", "failed", 1} for row in core)
    known = passed + failed
    token_values = [row["token_count"] for row in core if isinstance(row.get("token_count"), int)]
    event_counts = {
        name: sum(row.get("event") == name for row in core)
        for name in (
            "review_overturn",
            "retry",
            "timeout",
            "evidence_gap",
            "post_merge_regression",
        )
    }
    blocker_counts = {
        name: sum(row.get("blocker_class") == name for row in core)
        for name in ("product", "environment", "permission", "evidence", "dependency", "workflow")
    }
    all_event_counts: dict[str, int] = {}
    for row in core:
        event = row.get("event")
        if isinstance(event, str):
            all_event_counts[event] = all_event_counts.get(event, 0) + 1
    task_ids = {row.get("task_id") for row in core if isinstance(row.get("task_id"), str)}
    run_ids = {row.get("run_id") for row in core if isinstance(row.get("run_id"), str)}
    blocked_tasks = {
        row.get("task_id") for row in core
        if row.get("result") == "blocked" and isinstance(row.get("task_id"), str)
    }
    recovered_tasks = {
        task for task in blocked_tasks
        if any(
            later.get("task_id") == task
            and later.get("result") == "pass"
            and later.get("recorded_at", 0) > row.get("recorded_at", 0)
            for row in core if row.get("task_id") == task
            for later in core
        )
    }
    return {
        "schema": 1,
        "events": len(filtered),
        "core_events": len(core),
        "reported_events": len(reported),
        "passed": passed,
        "failed": failed,
        "blocked": sum(row.get("result") == "blocked" for row in core),
        "flaky": sum(row.get("result") == "flaky" for row in core),
        "unknown_results": sum(row.get("result") == "unknown" for row in core),
        "success_rate": passed / known if known else None,
        "known_result_success_rate": passed / known if known else None,
        "all_event_pass_rate": passed / len(core) if core else None,
        "blocked_rate": sum(row.get("result") == "blocked" for row in core) / len(core) if core else None,
        "token_count_total": sum(token_values) if token_values else None,
        "token_count_unknown": sum(row.get("token_count") is None for row in core),
        "review_overturns": event_counts["review_overturn"],
        "retries": event_counts["retry"] + sum(row.get("attempt", 0) > 0 for row in core),
        "timeouts": event_counts["timeout"] + sum(row.get("timed_out") is True for row in core),
        "evidence_gaps": event_counts["evidence_gap"],
        "post_merge_regressions": event_counts["post_merge_regression"],
        "blockers_by_class": blocker_counts,
        "main_agent_product_edits": sum(row.get("event") == "main_agent_product_edit" for row in core),
        "user_continue_nudges": sum(row.get("event") == "user_continue_nudge" for row in core),
        "user_process_corrections": sum(row.get("event") == "user_process_correction" for row in core),
        "recovery_path_misses": sum(row.get("event") == "recovery_path_miss" for row in core),
        "automatic_events": sum(row.get("source") == "pipeline_tools" for row in core),
        "event_counts": dict(sorted(all_event_counts.items())),
        "task_counts": dict(sorted({
            str(key): sum(row.get("task_id") == key for row in core)
            for key in task_ids
        }.items())),
        "run_counts": dict(sorted({
            str(key): sum(row.get("run_id") == key for row in core)
            for key in run_ids
        }.items())),
        "terminal_task_count": len({row.get("task_id") for row in core if _metric_bool(row.get("terminal")) and row.get("task_id")} ),
        "terminal_gate_pass_count": sum(row.get("event") == "gate_pre_merge" and row.get("result") == "pass" for row in core if _metric_bool(row.get("terminal"))),
        "terminal_unresolved_blocked_count": sum(row.get("result") == "blocked" for row in core if _metric_bool(row.get("terminal"))),
        "blocked_attempts": sum(row.get("result") == "blocked" for row in core),
        "blocked_task_count": len(blocked_tasks),
        "recovered_blocked_task_count": len(recovered_tasks),
        "recovery_rate": len(recovered_tasks) / len(blocked_tasks) if blocked_tasks else None,
        "unresolved_blocked_count": len(blocked_tasks - recovered_tasks),
        "terminal_state_unknown_count": sum(row.get("terminal") is None for row in core),
        "filters": {"task_id": task_id, "run_id": run_id, "terminal_only": terminal_only, "include_derived": include_derived},
    }


def _safe_version(value: str) -> str:
    match = re.search(r"v?(\d+(?:\.\d+){0,2})", value or "")
    return match.group(1) if match else "unknown"


def runtime_preflight(
    root: Path,
    expected_node: str | None = None,
    expected_pnpm: str | None = None,
    required_commands: list[str] | None = None,
    timeout: float = 20,
) -> dict[str, Any]:
    """Check the runtime before dispatching an executor or reviewer."""
    if not root.is_dir():
        return {"status": "blocked", "blocker_class": "environment", "errors": ["working directory does not exist"]}
    checks: dict[str, Any] = {}
    errors: list[str] = []
    commands = ("node", "pnpm.cmd", "git") + tuple(required_commands or []) if os.name == "nt" else ("node", "pnpm", "git") + tuple(required_commands or [])
    for name in commands:
        try:
            result = subprocess.run(
                [name, "--version"] if name not in {"git"} else [name, "--version"],
                cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            checks[name] = "missing"
            errors.append(f"{name} unavailable")
            continue
        version = _safe_version((result.stdout or result.stderr).strip())
        logical_name = "pnpm" if name == "pnpm.cmd" else name
        checks[logical_name] = version if result.returncode == 0 else "unavailable"
        if result.returncode != 0:
            errors.append(f"{name} returned {result.returncode}")
    if expected_node and checks.get("node") != _safe_version(expected_node):
        errors.append("node version mismatch")
    if expected_pnpm and checks.get("pnpm") != _safe_version(expected_pnpm):
        errors.append("pnpm version mismatch")
    return {
        "status": "pass" if not errors else "blocked",
        "blocker_class": None if not errors else "environment",
        "checks": checks,
        "errors": errors,
    }


def capability_handshake(
    root: Path,
    role: str,
    workflow_directory: Path,
    product_write_allowed: bool = False,
    expected_node: str | None = None,
    expected_pnpm: str | None = None,
    required_commands: list[str] | None = None,
) -> dict[str, Any]:
    """Create a bounded, machine-readable agent capability handshake."""
    root = Path(root).resolve()
    canonical, path_error = _canonical_workflow_directory(root, Path(workflow_directory))
    if path_error:
        return {
            "schema": 1,
            "role": role,
            "status": "blocked",
            "checks": {"repository_read": root.is_dir(), "workflow_write": False, "product_write": product_write_allowed, "runtime": False},
            "runtime": {"status": "unverified", "errors": []},
            "errors": [path_error],
        }
    runtime = runtime_preflight(root, expected_node, expected_pnpm, required_commands)
    checks = {
        "repository_read": root.is_dir(),
        "workflow_write": canonical is not None and (canonical.is_dir() or canonical.parent.is_dir()),
        "product_write": product_write_allowed,
        "runtime": runtime["status"] == "pass",
    }
    errors = list(runtime.get("errors", []))
    if not checks["repository_read"]:
        errors.append("repository unavailable")
    if not checks["workflow_write"]:
        errors.append("workflow directory is not writable")
    if role == "reviewer" and product_write_allowed:
        errors.append("reviewer product write must be denied")
    result = {
        "schema": 1,
        "role": role,
        "status": "pass" if not errors else "blocked",
        "checks": checks,
        "runtime": runtime,
        "errors": errors,
    }
    assert canonical is not None
    canonical.mkdir(parents=True, exist_ok=True)
    (canonical / "capability-handshake.json").write_text(
        json.dumps(result, ensure_ascii=True, sort_keys=True), encoding="utf-8"
    )
    return result


def lifecycle_status(root: Path, task_id: str, evidence_directory: Path) -> dict[str, Any]:
    """Derive the next safe workflow phase from current machine evidence."""
    errors: list[str] = []
    observed: list[dict[str, Any]] = []
    if not root.is_dir():
        return {
            "phase": "recovery",
            "status": "blocked",
            "errors": ["working directory does not exist"],
            "blockers": [{"class": "environment", "reason": "working directory does not exist"}],
            "next_actions": [],
            "unverified": ["repository identity", "task evidence"],
        }
    if not evidence_directory.exists():
        observed.append({"fact": "evidence_directory", "value": "not_created"})
    reports = {
        name: (evidence_directory / name).is_file()
        for name in REPORT_NAMES
    }
    machine_results = {
        name: (evidence_directory / name).is_file()
        for name in ("executor-result.json", "reviewer-result.json", "final-result.json")
    }
    observed.append({"fact": "machine_results", "value": machine_results})
    observed.append({"fact": "evidence_reports", "value": reports})
    if machine_results["final-result.json"] or reports["final-check.md"]:
        phase = "merge"
    elif machine_results["reviewer-result.json"] or reports["review-report.md"]:
        phase = "final-check"
    elif machine_results["executor-result.json"] or reports["executor-report.md"]:
        phase = "review"
    else:
        phase = "executor"
    blockers: list[dict[str, str]] = []
    if errors:
        blockers.append({"class": "evidence", "reason": errors[0]})
    next_actions_by_phase = {
        "executor": ["dispatch_executor"],
        "review": ["dispatch_reviewer"],
        "final-check": ["run_final_check"],
        "merge": ["run_gate_pre_merge", "merge_branch_in_main_worktree"],
    }
    if blockers:
        status = "blocked"
        next_actions: list[str] = ["reconcile_evidence"]
    else:
        status = "ready"
        next_actions = next_actions_by_phase[phase]
    return {
        "schema": 1,
        "command": "lifecycle.status",
        "task_id": task_id,
        "phase": phase,
        "status": status,
        "observed": observed,
        "errors": errors,
        "blockers": blockers,
        "next_actions": next_actions,
        "forbidden_actions": ["merge_branch_in_main_worktree"] if phase != "merge" else [],
        "unverified": [] if phase == "merge" else ["current phase acceptance evidence"],
    }


def _json_file(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _file_sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def git_identity(root: Path) -> dict[str, str | None]:
    root = Path(root).resolve()
    rc_head, head = git(root, "rev-parse", "--verify", "HEAD", redact_output=False)
    rc_branch, branch = git(root, "branch", "--show-current", redact_output=False)
    rc_worktree, worktree = git(root, "rev-parse", "--show-toplevel", redact_output=False)
    return {
        "head": head.strip() if rc_head == 0 else None,
        "branch": branch.strip() if rc_branch == 0 else None,
        "worktree": str(Path(worktree.strip()).resolve()) if rc_worktree == 0 and worktree.strip() else None,
    }


def retained_evidence_snapshot(directory: Path) -> dict[str, str]:
    return {
        name: _file_sha256(directory / name) or ""
        for name in RETAINED_EVIDENCE_NAMES
        if name != "finalization.json" and (directory / name).is_file()
    }


def verify_finalization_snapshot(directory: Path, marker: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    expected = marker.get("retained_sha256")
    if not isinstance(expected, dict) or not expected:
        errors.append("finalization retained evidence snapshot is missing")
    elif expected != retained_evidence_snapshot(directory):
        errors.append("finalization retained evidence hash mismatch")
    identity = marker.get("identity")
    if not isinstance(identity, dict):
        errors.append("finalization identity snapshot is missing")
    else:
        current = git_identity(root or _evidence_root(directory))
        for key in ("head", "branch", "worktree"):
            recorded = identity.get(key)
            if key == "worktree" and isinstance(recorded, str):
                recorded = str(Path(recorded).resolve())
            if recorded != current.get(key):
                errors.append(f"finalization {key} is stale")
    return errors


def _contract_from_text(text: str) -> dict[str, Any] | None:
    match = re.search(r"```pipeline-contract[ \t]*\r?\n(.*?)\r?\n```", text, re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _planning_requirements_sha256(root: Path, task_id: str | None) -> str | None:
    """Return the implement-plan hash recorded for a task at planning time."""
    planning = active_pipeline_dir(Path(root)) / "planning"
    if not planning.is_dir():
        return None
    for name in ("dispatch.json", "lifecycle.json", "result.json"):
        for path in sorted(planning.glob(f"*/{name}")):
            value = _json_file(path)
            if not isinstance(value, dict):
                continue
            if value.get("task_id") not in (None, task_id):
                continue
            candidates = [value.get("requirements_sha256")]
            identity = value.get("identity")
            if isinstance(identity, dict):
                candidates.append(identity.get("requirements_sha256"))
            for digest in candidates:
                if isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                    return digest
    return None


def _goal_evidence_files(directory: Path) -> list[Path]:
    """Return the goal evidence file, preferring goal.json over the legacy name."""
    return [directory / "goal.json", directory / "implement-plan.json"]


def _recorded_goal_sha256(root: Path, task_id: str | None) -> str | None:
    """Return the goal hash persisted in the task evidence directory."""
    if not task_id:
        return None
    directory = active_pipeline_dir(Path(root)) / task_id
    for path in _goal_evidence_files(directory):
        value = _json_file(path)
        if not isinstance(value, dict):
            continue
        if value.get("task_id") not in (None, task_id):
            continue
        digest = value.get("sha256")
        if isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            return digest
    return None


def goal_status(
    root: Path, contract: dict[str, Any], task_id: str | None = None
) -> tuple[list[str], str | None, str | None, list[str]]:
    """Compare the recorded and live goal hashes for a frozen contract.

    Returns ``(errors, recorded, observed, unverified)``.  The recorded value
    comes from the contract, else from the planning record, else from the task
    evidence directory; a drift error instructs re-planning.  A task with no
    recorded hash is reported as unverified instead of silently passing.
    Schema 4 binds the ``goal`` field; schema 1-3 keep the legacy
    ``implement_plan`` field read-only.
    """
    root = Path(root)
    goal = contract.get("goal")
    legacy_plan = contract.get("implement_plan")
    if isinstance(goal, dict):
        label, relative, document = "goal", "docs/goal.md", goal
    elif isinstance(legacy_plan, dict):
        label, relative, document = "implement-plan", "implement-plan.md", legacy_plan
    elif contract.get("schema") == 4:
        label, relative, document = "goal", "docs/goal.md", None
    else:
        label, relative, document = "implement-plan", "implement-plan.md", None
    recorded: str | None = None
    if isinstance(document, dict):
        path_value = document.get("path")
        if isinstance(path_value, str) and path_value.strip():
            relative = path_value.strip()
        digest = document.get("sha256")
        if isinstance(digest, str) and digest.strip():
            recorded = digest.strip()
    if not _validate_evidence_ref(relative):
        return [f"{label} path is not project-relative: {relative}"], recorded, None, []
    if recorded is None and task_id:
        recorded = _planning_requirements_sha256(root, task_id)
    if recorded is None and task_id:
        recorded = _recorded_goal_sha256(root, task_id)
    observed = _file_sha256(root / relative)
    if observed is None:
        if recorded:
            return [f"{label} is missing or unreadable: {relative}"], recorded, None, []
        return [], None, None, [f"{label} hash unrecorded and requirements doc unreadable: {relative}"]
    if recorded and recorded != observed:
        return [
            f"{label} hash drift: recorded "
            f"{recorded} but observed {observed}; requirements changed after planning, re-plan before continuing"
        ], recorded, observed, []
    if recorded is None:
        return [], None, observed, [f"{label} hash unrecorded: {relative}"]
    return [], recorded, observed, []


# Legacy name retained for callers that still import it.
implement_plan_status = goal_status


def _recorded_task_sheet_sha256(root: Path, task_id: str | None) -> str | None:
    """Return the task-sheet hash persisted next to the goal hash."""
    if not task_id:
        return None
    directory = active_pipeline_dir(Path(root)) / task_id
    for path in _goal_evidence_files(directory):
        value = _json_file(path)
        if not isinstance(value, dict):
            continue
        if value.get("task_id") not in (None, task_id):
            continue
        digest = value.get("task_sheet_sha256")
        if isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            return digest
    return None


def _record_goal_hash(
    root: Path,
    task_id: str,
    observed: str | None,
    task_sheet_sha256: str | None = None,
    *,
    legacy: bool = False,
    task_sheet_contract: dict[str, Any] | None = None,
) -> None:
    """Persist observed freeze hashes so later stages can enforce them.

    Schema 4 tasks record goal.json; legacy schema 1-3 tasks keep writing the
    implement-plan.json evidence file so historical contracts stay readable.
    The contract of the observed task sheet is snapshotted next to its hash so a
    later amendment can diff against the exact revision it replaces.
    """
    if not observed and not task_sheet_sha256:
        return
    directory = active_pipeline_dir(Path(root)) / task_id
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    name = "implement-plan.json" if legacy else "goal.json"
    existing = _json_file(directory / name)
    value: dict[str, Any] = dict(existing) if isinstance(existing, dict) else {}
    value["schema"] = 1
    value["task_id"] = task_id
    if observed:
        value["sha256"] = observed
    if task_sheet_sha256:
        value["task_sheet_sha256"] = task_sheet_sha256
    if isinstance(task_sheet_contract, dict) and task_sheet_contract:
        value["task_sheet_contract"] = task_sheet_contract
    _write_log(directory / name, json.dumps(value, ensure_ascii=True, sort_keys=True))


# Legacy name retained for callers that still reference it.
_record_implement_plan_hash = _record_goal_hash


def _task_sheet_contract(root: Path, task_id: str | None) -> dict[str, Any] | None:
    if not task_id:
        return None
    sheet = Path(root) / "docs" / "tasks" / f"{task_id}.md"
    if not sheet.is_file():
        return None
    contract, errors = load_contract(sheet)
    return None if errors or not isinstance(contract, dict) else contract


def _acceptance_test_ref_target(value: Any) -> tuple[str, str | None] | None:
    """Split a test_ref into its file path and optional Class.method target.

    The accepted grammar is ``path/to/file.py: Class.method``.  A bare path is
    valid and carries no position claim; only the text after the first colon is
    treated as a symbol target.
    """
    if not isinstance(value, str):
        return None
    head, separator, tail = value.partition(":")
    path = head.strip().replace(chr(92), "/")
    if not path:
        return None
    if not separator:
        return path, None
    target = tail.strip()
    if not target:
        return path, None
    target = target.split()[0].rstrip("().,;")
    return path, target or None


def _python_symbols(text: str) -> tuple[set[str], set[str]]:
    """Return the class names and ``Class.method`` pairs declared in source."""
    import ast

    classes: set[str] = set()
    methods: set[str] = set()
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return classes, methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.add(node.name)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(f"{node.name}.{child.name}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.add(node.name)
    return classes, methods


def _acceptance_test_ref_position_errors(root: Path, contract: dict[str, Any]) -> list[str]:
    """Verify the test_ref of every acceptance test names a real symbol.

    A test_ref that names a method must resolve to a declaration that exists in
    the named file; a test_ref that names only a path makes no position claim
    and is left to the planning-time placement check.
    """
    errors: list[str] = []
    tests = contract.get("acceptance_tests")
    if not isinstance(tests, list):
        return errors
    for index, item in enumerate(tests, start=1):
        if not isinstance(item, dict):
            continue
        target = _acceptance_test_ref_target(item.get("test_ref"))
        if target is None:
            continue
        path, symbol = target
        test_id = item.get("id") if isinstance(item.get("id"), str) else f"#{index}"
        if symbol is None:
            continue
        candidate = (root / path).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            errors.append(f"acceptance test {test_id} test_ref {path} escapes the project root")
            continue
        if not candidate.is_file():
            errors.append(f"acceptance test {test_id} test_ref file does not exist: {path}")
            continue
        classes, methods = _python_symbols(candidate.read_text(encoding="utf-8", errors="replace"))
        if "." in symbol:
            if symbol not in methods:
                errors.append(
                    f"acceptance test {test_id} test_ref method is absent from {path}: {symbol}"
                )
        elif symbol not in classes and symbol not in methods:
            errors.append(
                f"acceptance test {test_id} test_ref method is absent from {path}: {symbol}"
            )
    return errors


def write_dispatch(root: Path, dispatch: dict[str, Any], output: Path) -> Path:
    """Validate and atomically write a structured executor/reviewer dispatch."""
    required = ("schema", "task_id", "role", "round", "root", "worktree", "branch", "evidence_dir", "permissions", "output")
    missing = [field for field in required if field not in dispatch]
    if missing:
        raise ValueError(f"dispatch missing fields: {', '.join(missing)}")
    if dispatch["schema"] != 1 or dispatch["role"] not in {"executor", "reviewer"}:
        raise ValueError("invalid dispatch schema or role")
    permissions = dispatch["permissions"]
    if not isinstance(permissions, dict) or permissions.get("write_workflow") is not True:
        raise ValueError("dispatch must allow workflow writes")
    if dispatch["role"] == "reviewer" and permissions.get("write_product") is not False:
        raise ValueError("reviewer product writes must be false")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(dispatch, ensure_ascii=True, sort_keys=True), encoding="utf-8")
    os.replace(temporary, output)
    return output


def verify_structured_result(
    path: Path,
    expected_task_id: str,
    expected_role: str,
    evidence_directory: Path | None = None,
    *,
    strict: bool = False,
    expected_acceptance_ids: set[str] | None = None,
) -> list[str]:
    """Validate a machine result without interpreting semantic claims.

    Evidence references are resolved against the result's directory by default;
    callers may provide an explicit evidence directory for compatibility with
    result files stored elsewhere.
    """
    value = _json_file(path)
    evidence_directory = Path(evidence_directory) if evidence_directory is not None else Path(path).parent
    if value is None:
        return ["result is missing or invalid JSON"]
    errors: list[str] = []
    for field in ("schema", "task_id", "role", "status", "acceptance", "unverified"):
        if field not in value:
            errors.append(f"missing field: {field}")
    if value.get("schema") != 1:
        errors.append("schema must be 1")
    if value.get("task_id") != expected_task_id:
        errors.append("task identity mismatch")
    if resolve_result_role(value.get("role")) != resolve_result_role(expected_role):
        errors.append("role mismatch")
    result_status = normalize_status(value.get("status"), RESULT_STATUSES)
    if result_status is None:
        errors.append("invalid status")
    top_exit_code = value.get("exit_code", 0)
    if strict and (not isinstance(top_exit_code, int) or isinstance(top_exit_code, bool)):
        errors.append("exit_code must be an integer")
    elif strict and result_status == "pass" and top_exit_code != 0:
        errors.append("PASS result exit_code must equal expected_exit_code 0")
    if not isinstance(value.get("acceptance"), list) or not value.get("acceptance"):
        errors.append("acceptance must be a non-empty array")
    if not isinstance(value.get("unverified"), list):
        errors.append("unverified must be an array")
    for index, item in enumerate(value.get("acceptance", []), start=1):
        if not isinstance(item, dict):
            errors.append(f"acceptance {index} must be an object")
            continue
        for field in ("id", "status", "exit_code", "evidence_refs"):
            if field not in item:
                errors.append(f"acceptance {index} missing field: {field}")
        if not isinstance(item.get("id"), str) or not item.get("id", "").strip():
            errors.append(f"acceptance {index} id must be a non-empty string")
        acceptance_status = normalize_status(item.get("status"), ACCEPTANCE_STATUSES)
        if acceptance_status is None:
            errors.append(f"acceptance {index} has invalid status")
        elif strict and result_status == "pass" and acceptance_status != "pass":
            errors.append(f"acceptance {index} must be PASS when result status is PASS")
        exit_code = item.get("exit_code")
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            errors.append(f"acceptance {index} exit_code must be an integer")
        elif strict and result_status == "pass" and exit_code != 0:
            errors.append(f"acceptance {index} exit_code must equal expected_exit_code 0")
        references = item.get("evidence_refs")
        if not isinstance(references, list) or not references:
            errors.append(f"acceptance {index} evidence_refs must be a non-empty array")
        else:
            for reference in references:
                if not _evidence_file_exists(evidence_directory, reference):
                    errors.append(f"acceptance {index} evidence_ref is missing or not relative: {reference}")
        if expected_acceptance_ids is not None and isinstance(item.get("id"), str) and item.get("id") not in expected_acceptance_ids:
            errors.append(f"acceptance {index} id is not in the current task contract: {item.get('id')}")
    if strict and expected_acceptance_ids is not None:
        actual_ids = {item.get("id") for item in value.get("acceptance", []) if isinstance(item, dict)}
        missing_ids = expected_acceptance_ids - actual_ids
        for acceptance_id in sorted(missing_ids):
            errors.append(f"missing acceptance id from current task contract: {acceptance_id}")
    return errors


def create_derived_dispatch(
    root: Path,
    parent_task_sheet: Path,
    parent_task_id: str,
    parent_branch: str,
    parent_commit: str,
    child_task_id: str,
    child_branch: str,
    *,
    continuation: bool = False,
) -> dict[str, Any]:
    """Create an independent derived task from an explicit frozen parent commit.

    The child is created in a fresh worktree at the parent commit.  Parent files,
    evidence, and history are never copied or rewritten; the child sheet and
    evidence directory are created only in the child worktree.
    """
    root = Path(root).resolve()
    parent_task_sheet = Path(parent_task_sheet).resolve()
    if not _safe_task_identifier(parent_task_id) or not _safe_task_identifier(child_task_id):
        return {
            "schema": 1, "command": "dispatch.derived-create", "status": "blocked",
            "parent_task_id": parent_task_id, "task_id": child_task_id,
            "errors": [
                "task identifiers must contain only letters, digits, dot, underscore, and hyphen",
                "child task sheet is not a valid contract: unsafe task identifier",
            ],
            "blockers": [{"class": "workflow", "category": "contract", "reason": "unsafe task identifier"}],
            "artifacts": [], "next_actions": ["reconcile task identity"],
        }
    target = root / ".worktrees" / child_task_id
    result: dict[str, Any] = {
        "schema": 1, "command": "dispatch.derived-create", "status": "blocked",
        "parent_task_id": parent_task_id, "parent_branch": parent_branch,
        "parent_commit": parent_commit, "task_id": child_task_id,
        "branch": child_branch, "root": str(root), "worktree": str(target),
        "errors": [], "blockers": [], "artifacts": [],
        "next_actions": ["reconcile parent identity"],
    }

    def blocked(reason: str, category: str = "identity") -> dict[str, Any]:
        result["errors"].append(reason)
        result["blockers"].append({"class": "workflow", "category": category, "reason": reason})
        return result

    def rollback(reason: str, category: str = "freeze") -> dict[str, Any]:
        outcome = blocked(reason, category)
        if target.exists():
            rc, output = git(root, "worktree", "remove", "--force", str(target), redact_output=False, timeout=60)
            if rc:
                detail = next((line.strip() for line in output.splitlines() if line.strip()), "git worktree remove failed")
                outcome["errors"].append(f"child worktree rollback failed: {detail}")
                outcome["blockers"].append({"class": "workflow", "category": "git", "reason": "child worktree rollback failed"})
        branch_rc, _ = git(root, "rev-parse", "--verify", f"refs/heads/{child_branch}", redact_output=False)
        if branch_rc == 0:
            rc, output = git(root, "branch", "-D", child_branch, redact_output=False)
            if rc:
                detail = next((line.strip() for line in output.splitlines() if line.strip()), "git branch -D failed")
                outcome["errors"].append(f"child branch rollback failed: {detail}")
                outcome["blockers"].append({"class": "workflow", "category": "git", "reason": "child branch rollback failed"})
        return outcome

    if not parent_task_id or not child_task_id or parent_task_id == child_task_id:
        return blocked("parent and child task ids must be distinct", "contract")
    if not parent_branch or not child_branch or parent_branch == child_branch:
        return blocked("parent and child branches must be distinct", "branch")
    if continuation and "continuation" not in child_task_id:
        return blocked("continuation task id must contain continuation", "contract")
    if target.exists():
        return blocked("child worktree target is occupied", "path")
    rc, actual_root = git(root, "rev-parse", "--show-toplevel", redact_output=False)
    if rc or Path(actual_root.strip()).resolve() != root:
        return blocked("root is not the Git worktree root", "root")
    rc, current_branch = git(root, "branch", "--show-current", redact_output=False)
    if rc or current_branch.strip() != parent_branch:
        return blocked("parent branch does not match current worktree", "identity")
    rc, current_head = git(root, "rev-parse", "HEAD", redact_output=False)
    if rc or current_head.strip() != parent_commit:
        return blocked("parent commit does not match current HEAD", "baseline")
    contract, errors = load_contract(parent_task_sheet)
    if contract is None or errors:
        return blocked("parent task sheet is not a valid contract: " + "; ".join(errors), "freeze")
    if contract.get("task_id") != parent_task_id:
        return blocked("parent task sheet task_id mismatch", "identity")
    try:
        relative_sheet = parent_task_sheet.relative_to(root).as_posix()
    except ValueError:
        return blocked("parent task sheet is outside repository root", "path")
    parent_task_type = contract.get("task_type")
    if not isinstance(parent_task_type, str) or not parent_task_type.strip():
        return blocked("parent task sheet is missing task_type; derived_from.parent_task_type cannot be resolved", "contract")
    rc, _ = git(root, "ls-files", "--error-unmatch", relative_sheet)
    if rc:
        return blocked("parent task sheet is not committed", "freeze")
    rc, blob = git(root, "show", f"{parent_commit}:{relative_sheet}", redact_output=False)
    if rc or not blob.strip():
        return blocked("parent task sheet is absent from explicit parent commit", "freeze")
    rc, status = git(root, "status", "--porcelain=v1", "--untracked-files=all", redact_output=False)
    if rc or any(line[3:].strip().strip('\\\"') == relative_sheet for line in status.splitlines() if len(line) >= 4):
        return blocked("parent task sheet is uncommitted", "freeze")
    rc, listing = git(root, "worktree", "list", "--porcelain", redact_output=False)
    if rc:
        return blocked("unable to inspect worktree list", "git")
    if f"branch refs/heads/{child_branch}" in listing or str(target) in listing:
        return blocked("duplicate child worktree or branch conflict", "conflict")
    rc, branches = git(root, "branch", "--list", child_branch, redact_output=False)
    if rc or branches.strip():
        return blocked("child branch already exists", "branch")

    child_sheet = target / "docs" / "tasks" / f"{child_task_id}.md"
    evidence = target / ".pipeline" / child_task_id
    try:
        rc, output = git(root, "worktree", "add", "-b", child_branch, str(target), parent_commit, redact_output=False, timeout=60)
        if rc:
            return rollback("child worktree creation failed", "git")
        child_contract = dict(contract)
        child_contract["task_id"] = child_task_id
        child_contract["task_type"] = "derived"
        child_contract["dependencies"] = list(child_contract.get("dependencies", [])) + [parent_task_id]
        child_contract["derived_from"] = {
            "task_id": parent_task_id,
            "commit": parent_commit,
            "branch": parent_branch,
            "parent_task_type": parent_task_type.strip(),
        }
        child_sheet.parent.mkdir(parents=True, exist_ok=True)
        child_sheet.write_text(
            f"# {child_task_id}：派生任务单\n\n<!-- Task ID: {child_task_id} -->\n\n"
            "```pipeline-contract\n" + json.dumps(child_contract, ensure_ascii=True, indent=2) + "\n```\n",
            encoding="utf-8",
        )
        child_errors = validate_task(child_sheet)
        if child_errors:
            return rollback("child task sheet is not a valid contract: " + "; ".join(child_errors), "contract")
        evidence.mkdir(parents=True, exist_ok=False)
        relative_child = f"docs/tasks/{child_task_id}.md"
        rc, _ = git(target, "add", relative_child, redact_output=False)
        if rc:
            return rollback("child task sheet could not be staged", "freeze")
        rc, _ = git(target, "commit", "-m", f"freeze derived task sheet {child_task_id}", redact_output=False, timeout=60)
        if rc:
            return rollback("child task sheet commit failed", "freeze")
        rc, _ = git(target, "ls-files", "--error-unmatch", relative_child, redact_output=False)
        if rc:
            return rollback("child task sheet is not committed", "freeze")
    except (OSError, ValueError) as error:
        return rollback(f"child dispatch creation failed: {type(error).__name__}", "git")

    rc1, actual_root = git(target, "rev-parse", "--show-toplevel", redact_output=False)
    rc2, actual_branch = git(target, "branch", "--show-current", redact_output=False)
    rc3, fork_point = git(target, "rev-parse", "HEAD^", redact_output=False)
    if rc1 or rc2 or rc3 or Path(actual_root.strip()).resolve() != target or actual_branch.strip() != child_branch or fork_point.strip() != parent_commit:
        return rollback("child post-create identity verification failed", "identity")
    result.update({
        "status": "pass",
        "identity": {"parent_task_id": parent_task_id, "parent_branch": parent_branch,
                     "parent_commit": parent_commit, "task_id": child_task_id,
                     "branch": child_branch, "worktree": str(target),
                     "baseline": parent_commit, "parent_evidence_reused": False},
        "child_task_sheet": str(child_sheet), "evidence_dir": str(evidence),
        "artifacts": [str(child_sheet), str(evidence)],
        "derived_from": {
            "task_id": parent_task_id,
            "commit": parent_commit,
            "branch": parent_branch,
            "parent_task_type": parent_task_type.strip(),
        },
        "next_actions": ["dispatch executor"],
    })
    return result


def create_worktree_dispatch(root: Path, task_sheet: Path, task_id: str, branch: str, baseline: str, *, role: str = "executor") -> dict[str, Any]:
    """Create and verify the unique frozen task worktree."""
    root, task_sheet = Path(root).resolve(), Path(task_sheet).resolve()
    target = root / ".worktrees" / task_id
    result = {"schema": 1, "command": "dispatch.worktree-create", "status": "blocked", "task_id": task_id, "role": role, "root": str(root), "worktree": str(target), "branch": branch, "baseline": baseline, "errors": [], "blockers": [], "artifacts": [], "unverified": [], "next_actions": ["reconcile identity"]}
    def blocked(reason: str, category: str = "identity") -> dict[str, Any]:
        result["errors"].append(reason); result["blockers"].append({"class": "workflow", "category": category, "reason": reason}); return result
    if role not in {"executor", "reviewer"}: return blocked("invalid dispatch role")
    contract, errors = load_contract(task_sheet)
    if contract is None or errors or contract.get("schema") not in {2, 3, 4}: return blocked("task sheet is not a valid frozen schema2/schema3/schema4 contract: " + "; ".join(errors or ["schema must be 2, 3 or 4"]), "freeze")
    if contract.get("task_id") != task_id: return blocked("task sheet task_id does not match dispatch task_id")
    plan_errors, _recorded_hash, observed_hash, plan_unverified = implement_plan_status(root, contract, task_id)
    if plan_errors: return blocked("; ".join(plan_errors), "drift")
    rc, actual = git(root, "rev-parse", "--show-toplevel", redact_output=False)
    if rc or Path(actual.strip()).resolve() != root: return blocked("root is not the Git worktree root", "root")
    rc, actual = git(root, "rev-parse", "HEAD", redact_output=False)
    if rc or actual.strip() != baseline: return blocked("baseline HEAD does not match requested baseline", "baseline")
    relative = task_sheet.relative_to(root).as_posix() if task_sheet.is_relative_to(root) else None
    if not relative: return blocked("task sheet is outside repository root", "path")
    rc, _ = git(root, "ls-files", "--error-unmatch", relative)
    if rc: return blocked("task sheet is not committed", "freeze")
    rc, status = git(root, "status", "--porcelain=v1", "--untracked-files=all", redact_output=False)
    if rc or any(line[3:].strip().strip('\\\"') == relative for line in status.splitlines() if len(line) >= 4): return blocked("task sheet is uncommitted", "freeze")
    rc, listing = git(root, "worktree", "list", "--porcelain", redact_output=False)
    if rc: return blocked("unable to inspect worktree list", "git")
    if str(target) in listing or f"branch refs/heads/{branch}" in listing: return blocked("duplicate worktree or branch conflict", "conflict")
    rc, branches = git(root, "branch", "--list", branch, redact_output=False)
    if rc or branches.strip(): return blocked("branch already exists", "branch")
    if target.exists(): return blocked("worktree target is occupied", "path")
    rc, _ = git(root, "worktree", "add", "-b", branch, str(target), baseline, redact_output=False, timeout=60)
    if rc:
        outcome = blocked("worktree creation failed", "git")
        if target.exists():
            remove_rc, remove_output = git(root, "worktree", "remove", "--force", str(target), redact_output=False, timeout=60)
            if remove_rc:
                detail = next((line.strip() for line in remove_output.splitlines() if line.strip()), "git worktree remove failed")
                outcome["errors"].append(f"worktree rollback failed: {detail}")
        branch_rc, _ = git(root, "rev-parse", "--verify", f"refs/heads/{branch}", redact_output=False)
        if branch_rc == 0:
            delete_rc, delete_output = git(root, "branch", "-D", branch, redact_output=False)
            if delete_rc:
                detail = next((line.strip() for line in delete_output.splitlines() if line.strip()), "git branch -D failed")
                outcome["errors"].append(f"branch rollback failed: {detail}")
        return outcome
    rc1, actual_root = git(target, "rev-parse", "--show-toplevel", redact_output=False); rc2, actual_branch = git(target, "branch", "--show-current", redact_output=False); rc3, actual_head = git(target, "rev-parse", "HEAD", redact_output=False)
    if rc1 or rc2 or rc3 or Path(actual_root.strip()).resolve() != target.resolve() or actual_branch.strip() != branch or actual_head.strip() != baseline: return blocked("post-create identity verification failed", "identity")
    result.update({"status": "pass", "identity": {"task_id": task_id, "role": role, "root": str(root), "worktree": str(target.resolve()), "branch": branch, "head": baseline, "task_sheet": str(task_sheet), "contract_schema": contract.get("schema"), "implement_plan_sha256": observed_hash}, "observed": ["worktree list before and after", "root", "branch", "HEAD", "path", "implement-plan hash"], "artifacts": [str(target)], "next_actions": ["dispatch using this exact worktree"]})
    result["unverified"] = plan_unverified
    _record_goal_hash(root, task_id, observed_hash, legacy=contract.get("schema") != 4)
    return result


def evidence_freshness(root: Path, evidence_directory: Path, result_path: Path | None = None) -> dict[str, Any]:
    """Compare result identity while allowing only task-evidence-only commits."""
    result = _json_file(result_path) if result_path else None
    errors: list[str] = []
    observed: list[dict[str, Any]] = []
    rc, head = git(root, "rev-parse", "HEAD")
    current_head = head.strip() if rc == 0 else None
    if current_head:
        observed.append({"fact": "head", "value": current_head})
    identity = result.get("identity", {}) if isinstance(result, dict) else {}
    task_id = result.get("task_id") if isinstance(result, dict) else None
    contract = _task_sheet_contract(root, task_id)
    plan_unverified: list[str] = []
    if contract is None:
        errors.append(f"implement-plan contract not found for task {task_id}; freshness cannot verify requirements drift")
        plan_unverified.append("implement-plan requirements drift")
    else:
        plan_errors, recorded_hash, observed_hash, plan_unverified = implement_plan_status(root, contract, task_id)
        observed.append({"fact": "implement_plan_recorded", "value": recorded_hash})
        observed.append({"fact": "implement_plan_observed", "value": observed_hash})
        errors.extend(plan_errors)
    product_head = identity.get("product_head") if isinstance(identity, dict) else None
    observed_at_commit = result.get("observed_at_commit") if isinstance(result, dict) else None
    if result is None:
        errors.append("structured result is missing")
    elif product_head:
        base_rc, base = git(root, "rev-parse", "--verify", f"{product_head}^{{commit}}")
        if base_rc != 0:
            errors.append("product HEAD is invalid")
        elif current_head:
            ancestor_rc, _ancestor = git(root, "merge-base", "--is-ancestor", product_head, current_head)
            if ancestor_rc != 0:
                errors.append("product HEAD is not an ancestor of current HEAD")
            else:
                diff_rc, diff = git(root, "diff", "--name-only", product_head, current_head, redact_output=False)
                changed_paths = [path.replace("\\", "/") for path in diff.splitlines() if path.strip()]
                # Metrics events are workflow metadata that may be committed to the
                # host project (see references/metrics-contract.md). scope_check
                # already exempts them; evidence_only must use the same basis or
                # every task that ran pipeline-tools flips to a false product drift.
                evidence_only = evidence_only_paths(root, evidence_directory, changed_paths)
                observed.append({"fact": "product_head", "value": product_head})
                observed.append({"fact": "changed_paths", "value": changed_paths})
                observed.append({"fact": "evidence_only", "value": evidence_only})
                if diff_rc != 0 or not evidence_only:
                    errors.append("product/test HEAD drifted")
    elif isinstance(observed_at_commit, str) and observed_at_commit.strip():
        # Revision-bound evidence: the commit it was observed at is a fact, and
        # HEAD moving on its own never invalidates it.  Only a change to a path
        # the task's operations verify does.
        observed_at = observed_at_commit.strip()
        rc, _ = git(root, "rev-parse", "--verify", f"{observed_at}^{{commit}}")
        if rc:
            errors.append("observed_at_commit is not a valid commit")
        elif current_head:
            changed = changed_paths_between(root, observed_at, current_head) or []
            resources = sheet_operation_resources(contract or {}, _evidence_acceptance_ids(result))
            touched = sorted({path for path in changed if any(_matches(path, pattern, root) for pattern in resources)})
            observed.append({"fact": "observed_at_commit", "value": observed_at})
            observed.append({"fact": "changed_paths", "value": changed})
            observed.append({"fact": "verified_resources", "value": resources})
            observed.append({"fact": "verified_paths_changed", "value": touched})
            if touched:
                errors.append("paths under verification changed after this evidence was produced")
    elif identity.get("head") and identity["head"] != current_head:
        errors.append("result HEAD is stale")
    evidence_refs: list[str] = []
    if result:
        for item in result.get("acceptance", []):
            if isinstance(item, dict):
                evidence_refs.extend(ref for ref in item.get("evidence_refs", []) if isinstance(ref, str))
    # acceptance[].evidence_refs use the same basis as commands[].evidence_ref:
    # bare names resolve against the task evidence directory, while explicit
    # .pipeline/... references still resolve from the project root.
    missing = [
        reference
        for reference in evidence_refs
        if not _evidence_file_exists(evidence_directory, reference)
    ]
    if missing:
        errors.append("evidence artifact missing")
    return {
        "schema": 1,
        "command": "evidence.freshness",
        "status": "pass" if not errors else "blocked",
        "observed": observed,
        "errors": errors,
        "blockers": [{"class": "evidence", "reason": error} for error in errors],
        "artifacts": [str(evidence_directory / "freshness.json")],
        "next_actions": [] if not errors else ["regenerate_structured_result"],
        "unverified": plan_unverified,
        "result_sha256": _file_sha256(result_path) if result_path else None,
    }


def role_scope_check(
    root: Path,
    role: str,
    product_patterns: list[str] | None = None,
    authorized: bool = False,
    task_id: str | None = None,
    baseline: str | None = None,
) -> list[str]:
    """Prevent the main agent from changing product files without authorization."""
    if role != "main-agent" or authorized:
        return []
    patterns = product_patterns or ["src/**", "packages/**", "apps/**", "lib/**", "app/**"]
    if task_id:
        contract = _task_sheet_contract(root, task_id)
        if isinstance(contract, dict):
            patterns = list(contract.get("allowed_paths") or patterns)
            forbidden = list(contract.get("forbidden_paths") or [])
        else:
            forbidden = []
    else:
        forbidden = []
    if baseline:
        rc, output = git(root, "diff", "--name-only", baseline, "HEAD", redact_output=False)
        if rc:
            return [output or "unable to inspect baseline"]
        paths = [path for path in output.splitlines() if path.strip()]
    else:
        rc, output = git(root, "status", "--porcelain=v1", "--untracked-files=all")
        if rc:
            return [output or "not a git repository"]
        paths = _status_paths(output)
    return [
        path for path in paths
        if any(_matches(path, pattern, root) for pattern in patterns)
        or any(_matches(path, pattern, root) for pattern in forbidden)
    ]


def import_opencode_session(root: Path, session_file: Path, task_id: str = "opencode-session") -> list[Path]:
    """Convert structured OpenCode export observations into local metric events.

    Only machine signals are counted: tool-call error states.  Prose in the
    transcript is never interpreted.
    """
    session = json.loads(session_file.read_text(encoding="utf-8"))
    if not isinstance(session, dict) or not isinstance(session.get("messages"), list):
        raise ValueError("invalid OpenCode session export")
    info = session.get("info", {}) if isinstance(session.get("info"), dict) else {}
    output: list[Path] = []
    tool_errors = 0
    task_errors = 0
    for message in session["messages"]:
        for part in message.get("parts", []):
            if not isinstance(part, dict):
                continue
            if part.get("type") == "tool" and isinstance(part.get("state"), dict) and part["state"].get("status") == "error":
                tool_errors += 1
            if part.get("type") == "tool" and part.get("tool") == "task" and isinstance(part.get("state"), dict) and part["state"].get("status") == "error":
                task_errors += 1
    def record(name: str, result: str, reason: str, blocker: str | None = None) -> None:
        output.append(metric_event(root, {
            "event": name, "confidence": "observed", "task_id": task_id, "result": result,
            "reason": reason, "blocker_class": blocker, "source": "opencode_session",
            "evidence_ref": None,
        }))
    if tool_errors:
        record("evidence_gap", "blocked", f"tool_errors_{tool_errors}", "evidence")
    if task_errors:
        record("retry", "blocked", f"subagent_errors_{task_errors}", "workflow")
    return output


def purge_metrics(root: Path) -> int:
    count = 0
    for directory in metrics_dirs(root):
        if not directory.is_dir():
            continue
        for pattern in ("*.json", "*.tmp"):
            for path in directory.glob(pattern):
                path.unlink()
                count += 1
    return count


def _machine_result_errors(directory: Path, phase: str) -> list[str]:
    """Require machine results alongside the human-readable Markdown reports.

    ``pre-merge`` requires all three results; ``post-merge`` requires the final
    result and only validates the other two when they are present.
    """
    errors: list[str] = []
    for name in MACHINE_RESULT_NAMES:
        path = directory / name
        if not path.is_file():
            if phase == "pre-merge" or name == "final-result.json":
                errors.append(f"missing {name}")
            continue
        if _json_file(path) is None:
            errors.append(f"{name} is not a readable JSON object")
    return errors


def _resolves_to_root(value: Any, root: Path) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    candidate = Path(value.strip())
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve() == root.resolve()
    except (OSError, ValueError):
        return False


def _post_merge_reverified_in_main_worktree(report: dict[str, Any] | None, root: Path) -> bool:
    """Return whether a passing command ran in the main worktree after merging.

    A per-command ``cwd`` is authoritative; when a producer omits it, the
    report-level ``worktree`` is used as the fallback.
    """
    if not isinstance(report, dict):
        return False
    report_worktree = report.get("worktree")
    commands = report.get("commands")
    if not isinstance(commands, list):
        return False
    for command in commands:
        if not isinstance(command, dict) or command.get("exit_code") != 0:
            continue
        if _resolves_to_root(command.get("cwd", report_worktree), root):
            return True
    return False


def gate_check(
    directory: Path,
    task_id: str,
    branch: str | None,
    phase: str,
    *,
    unverified: list[str] | None = None,
) -> list[str]:
    """Run evidence checks and the minimum phase-specific merge gates.

    ``unverified`` is an optional out-parameter. Reasons that cannot be
    machine-verified, such as a task that never recorded an implement-plan
    hash, are appended there instead of being reported as errors; only a
    genuine hash drift stays a hard error.
    """
    directory = _canonical_evidence_dir(directory)
    # Post-merge evidence is identified by the task id and the sheet revision: the
    # merge itself always adds product-path commits to the current head.
    errors = evidence_verify(directory, task_id, branch, "finalized" if phase == "post-merge" else "active")
    root = _evidence_root(directory)
    contract = _task_sheet_contract(root, task_id)
    if contract is None:
        errors.append(f"implement-plan contract not found for task {task_id}; gate cannot verify requirements drift")
    else:
        plan_errors, _recorded_hash, _observed_hash, plan_unverified = implement_plan_status(root, contract, task_id)
        errors.extend(plan_errors)
        if unverified is not None:
            unverified.extend(plan_unverified)
        errors.extend(_acceptance_test_ref_position_errors(root, contract))
    reports: dict[str, dict[str, Any]] = {}
    for name in REPORT_NAMES:
        value, parse_errors = _read_machine_evidence(directory / name)
        if not parse_errors and value is not None:
            reports[name] = value
            if phase == "post-merge" and value.get("schema") != 2:
                errors.append(f"{name} schema 1 is legacy/unverified and cannot support {phase} gate")

    errors.extend(_machine_result_errors(directory, phase))
    expected_acceptance_ids = {
        item.get("id") for item in (contract or {}).get("acceptance_tests", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    result_roles = {"executor-result.json": "executor", "reviewer-result.json": "reviewer", "final-result.json": "final"}
    for result_name, result_role in result_roles.items():
        result_path = directory / result_name
        if result_path.is_file() and (phase == "pre-merge" or result_name == "final-result.json"):
            errors.extend(
                f"{result_name}: {error}"
                for error in verify_structured_result(
                    result_path, task_id, result_role, directory,
                    strict=True, expected_acceptance_ids=expected_acceptance_ids,
                )
            )

    # Structural verification and a merge gate are intentionally separate:
    # a report may accurately say BLOCKED, but that must block merging.
    for name, value in reports.items():
        status = value.get("status")
        if phase == "pre-merge" and name in {"executor-report.md", "review-report.md", "final-check.md"}:
            if normalize_status(status, PRE_MERGE_REPORT_STATUSES) is None:
                errors.append(f"{name} status is not mergeable")
        if phase == "post-merge" and name != "executor-report.md" and normalize_status(status, POST_MERGE_REPORT_STATUSES) is None:
            errors.append(f"{name} status is not post-merge passing")
        for command in value.get("commands", []):
            if not isinstance(command, dict):
                continue
            exit_code = command.get("exit_code")
            expected = command.get("expected_exit_code")
            if expected is not None and (
                isinstance(expected, bool) or not isinstance(expected, int)
            ):
                errors.append(f"{name} command expected_exit_code must be an integer")
            elif expected is None:
                if exit_code != 0:
                    errors.append(f"{name} contains a non-zero command exit_code")
            elif isinstance(exit_code, bool) or exit_code != expected:
                errors.append(f"{name} command exit_code does not match declared expected_exit_code")

    if (root / ".git").exists() or (root / ".git").is_file():
        rc, _ = git(root, "diff", "--check")
        if rc:
            errors.append("git diff --check failed")
        rc, output = git(root, "ls-files", "-u")
        if rc:
            errors.append("unable to inspect conflict index")
        elif output.strip():
            errors.append("unmerged entries present")
        if phase == "post-merge":
            rc, _ = git(root, "rev-parse", "--verify", "HEAD")
            if rc:
                errors.append("merged HEAD unavailable")
            if not _post_merge_reverified_in_main_worktree(reports.get("final-check.md"), root):
                errors.append("post-merge re-verification in the main worktree is missing")
    return errors


# --- Task sheet revisions ---------------------------------------------------
# A task sheet is a versioned contract: revision 1 is the frozen sheet recorded
# by freeze_check, and every later revision is one append-only entry in
# .pipeline/<task-id>/amendments.json.  This module classifies and records
# amendments; it never generates or rewrites task sheet content.

AMENDMENT_SCHEMA = 1
AMENDMENT_WRITER_ROLE = "main-agent"
AMENDMENT_REQUEST_ROLES = ("main-agent", "executor", "reviewer")
# Identity fields describe which task this contract is; changing them would make
# the record describe a different task, so they are never amendable.
CONTRACT_IDENTITY_FIELDS = ("schema", "task_id", "task_type", "derived_from")
VERIFICATION_SURFACE_FIELDS = (
    "acceptance_tests",
    "allowed_paths",
    "forbidden_paths",
    "chain",
    "required_evidence_levels",
    "operations",
    "risk",
)
# A changed assertion target cannot be proven to be a tightening, so it is
# treated as a loosening and needs an adjudication reference.
LOOSENING_ACCEPTANCE_FIELDS = ("test_ref", "command_ref")
_SHA256_RE = re.compile(r"[0-9a-fA-F]{64}\Z")


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    return value


def task_sheet_candidates(root: Path, task_id: str) -> list[Path]:
    """Return the supported task-sheet locations in resolution order."""
    root = Path(root)
    pipeline = active_pipeline_dir(root)
    return [
        root / "docs" / "tasks" / f"{task_id}.md",
        pipeline / task_id / f"{task_id}.md",
        pipeline / "archive" / f"{task_id}.md",
    ]


def task_sheet_path(root: Path, task_id: str) -> Path | None:
    """Resolve a task sheet by id: docs/tasks, then evidence dir, then archive."""
    if not _safe_task_identifier(task_id):
        return None
    for candidate in task_sheet_candidates(root, task_id):
        if candidate.is_file():
            return candidate
    return None


def amendments_path(root: Path, task_id: str) -> Path:
    return active_pipeline_dir(Path(root)) / task_id / "amendments.json"


def read_amendments(root: Path, task_id: str) -> tuple[dict[str, Any] | None, list[str]]:
    """Read the append-only amendment record without rewriting it."""
    path = amendments_path(root, task_id)
    if not path.is_file():
        return None, []
    value = _json_file(path)
    if value is None:
        return None, ["amendments.json is missing or invalid JSON"]
    revisions = value.get("revisions")
    if value.get("schema") != AMENDMENT_SCHEMA or value.get("task_id") != task_id or not isinstance(revisions, list):
        return None, ["amendments.json identity or schema is invalid"]
    for index, record in enumerate(revisions, start=1):
        if not isinstance(record, dict):
            return None, [f"amendments.json revision {index} is not an object"]
        revision = record.get("revision")
        if isinstance(revision, bool) or not isinstance(revision, int) or revision != index + 1:
            return None, [f"amendments.json revision {index} is not in ascending order"]
        digest = record.get("sheet_sha256")
        if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            return None, [f"amendments.json revision {index} has no task sheet hash"]
    return value, []


def task_sheet_revision(root: Path, task_id: str) -> tuple[int, str | None]:
    """Return the current sheet revision and the hash it must match."""
    if not _safe_task_identifier(task_id):
        return 1, None
    record, errors = read_amendments(root, task_id)
    if errors or record is None or not record["revisions"]:
        return 1, _recorded_task_sheet_sha256(root, task_id)
    last = record["revisions"][-1]
    digest = last.get("sheet_sha256")
    return (
        last["revision"],
        digest if isinstance(digest, str) and _SHA256_RE.fullmatch(digest) else _recorded_task_sheet_sha256(root, task_id),
    )


def task_sheet_baseline_sha256(root: Path, task_id: str) -> str | None:
    """Return the hash the recorded revision of a task sheet must match."""
    return task_sheet_revision(root, task_id)[1]


def recorded_task_sheet_hashes(root: Path, task_id: str) -> set[str]:
    """Every task sheet hash the recorded amendment chain accounts for."""
    record, errors = read_amendments(root, task_id)
    if errors or record is None:
        return set()
    hashes: set[str] = set()
    for entry in record["revisions"]:
        for key in ("previous_sheet_sha256", "sheet_sha256"):
            value = entry.get(key)
            if isinstance(value, str) and _SHA256_RE.fullmatch(value):
                hashes.add(value)
    return hashes


def _goal_contract_snapshot(root: Path, task_id: str) -> dict[str, Any] | None:
    directory = active_pipeline_dir(Path(root)) / task_id
    for path in _goal_evidence_files(directory):
        value = _json_file(path)
        if not isinstance(value, dict) or value.get("task_id") not in (None, task_id):
            continue
        snapshot = value.get("task_sheet_contract")
        if isinstance(snapshot, dict) and snapshot:
            return snapshot
    return None


def _git_blob(root: Path, reference: str) -> bytes | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "show", reference],
            capture_output=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return completed.stdout if completed.returncode == 0 else None


def _previous_sheet_contract(root: Path, task_id: str, sheet: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Return the contract of the recorded revision the new one replaces."""
    record, _errors = read_amendments(root, task_id)
    if record and record["revisions"]:
        snapshot = record["revisions"][-1].get("sheet_contract")
        if isinstance(snapshot, dict) and snapshot:
            return snapshot, []
    snapshot = _goal_contract_snapshot(root, task_id)
    if snapshot is not None:
        return snapshot, []
    try:
        relative = Path(sheet).resolve().relative_to(Path(root).resolve()).as_posix()
    except (OSError, ValueError):
        return None, ["the task sheet is outside the project root"]
    blob = _git_blob(root, f"HEAD:{relative}")
    if blob is None:
        return None, ["the recorded revision of the task sheet is not available in Git"]
    contract = _contract_from_text(blob.decode("utf-8", "replace"))
    if not isinstance(contract, dict):
        return None, ["the recorded revision of the task sheet has no readable contract"]
    baseline = _recorded_task_sheet_sha256(root, task_id)
    if baseline:
        # Git stores line endings in its own form, so accept either the exact blob
        # or its CRLF translation before rejecting the recorded revision.
        digests = {
            hashlib.sha256(blob).hexdigest(),
            hashlib.sha256(blob.replace(b"\n", b"\r\n")).hexdigest(),
        }
        if baseline not in digests:
            return None, [
                "the task sheet at HEAD does not match the recorded revision; "
                "record the earlier change before amending"
            ]
    return contract, []


def _dependency_id(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        for key in ("task_id", "id"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _dependency_edges(root: Path, task_id: str) -> list[str] | None:
    sheet = task_sheet_path(root, task_id)
    if sheet is None:
        return None
    contract, errors = load_contract(sheet)
    if errors or not isinstance(contract, dict):
        return None
    return [item for item in (_dependency_id(entry) for entry in contract.get("dependencies", [])) if item]


def dependency_cycle(root: Path, task_id: str, dependencies: list[str]) -> list[str] | None:
    """Return the dependency path that closes a cycle, or None when it is acyclic.

    The amended task's own edges are the candidate dependency list; every other
    node is read from its on-disk sheet.
    """
    cache: dict[str, list[str] | None] = {}

    def edges(identifier: str) -> list[str]:
        if identifier == task_id:
            return list(dependencies)
        if identifier not in cache:
            cache[identifier] = _dependency_edges(root, identifier)
        return cache[identifier] or []

    stack: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> list[str] | None:
        if identifier in visiting:
            return [*stack[stack.index(identifier):], identifier]
        if identifier in visited:
            return None
        visiting.add(identifier)
        stack.append(identifier)
        for dependency in edges(identifier):
            found = visit(dependency)
            if found:
                return found
        stack.pop()
        visiting.discard(identifier)
        visited.add(identifier)
        return None

    return visit(task_id)


def _list_delta(before: Any, after: Any) -> dict[str, list[Any]]:
    previous = before if isinstance(before, list) else []
    current = after if isinstance(after, list) else []
    canonical_previous = [_canonical(item) for item in previous]
    canonical_current = [_canonical(item) for item in current]
    return {
        "added": [item for item, key in zip(current, canonical_current) if key not in canonical_previous],
        "removed": [item for item, key in zip(previous, canonical_previous) if key not in canonical_current],
    }


def _contract_changes(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Return the structural difference between two contract revisions."""

    def acceptance_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
        tests = contract.get("acceptance_tests")
        return {
            item["id"]: item
            for item in (tests if isinstance(tests, list) else [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    before_tests, after_tests = acceptance_map(previous), acceptance_map(current)
    modified: list[dict[str, Any]] = []
    for identifier in before_tests:
        if identifier not in after_tests:
            continue
        before, after = before_tests[identifier], after_tests[identifier]
        if _canonical(before) == _canonical(after):
            continue
        fields = {
            name: {"from": before.get(name), "to": after.get(name)}
            for name in sorted(set(before) | set(after))
            if _canonical(before.get(name)) != _canonical(after.get(name))
        }
        modified.append({"id": identifier, "fields": fields})

    def operation_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
        operations = contract.get("operations")
        return {
            item["id"]: item
            for item in (operations if isinstance(operations, list) else [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    before_operations, after_operations = operation_map(previous), operation_map(current)
    chain_before = previous.get("chain") if isinstance(previous.get("chain"), dict) else {}
    chain_after = current.get("chain") if isinstance(current.get("chain"), dict) else {}
    return {
        "acceptance_tests": {
            "added": [item for item in after_tests if item not in before_tests],
            "removed": [item for item in before_tests if item not in after_tests],
            "modified": modified,
        },
        "dependencies": _list_delta(
            [item for item in (_dependency_id(entry) for entry in previous.get("dependencies", [])) if item],
            [item for item in (_dependency_id(entry) for entry in current.get("dependencies", [])) if item],
        ),
        "allowed_paths": _list_delta(previous.get("allowed_paths"), current.get("allowed_paths")),
        "forbidden_paths": _list_delta(previous.get("forbidden_paths"), current.get("forbidden_paths")),
        "non_goals": _list_delta(previous.get("non_goals"), current.get("non_goals")),
        "risk": {"from": previous.get("risk"), "to": current.get("risk")},
        "required_evidence_levels": _list_delta(
            previous.get("required_evidence_levels"), current.get("required_evidence_levels")
        ),
        "chain": {
            "changed": _canonical(chain_before) != _canonical(chain_after),
            "segments": sorted(
                name for name in CHAIN_NAMES if _canonical(chain_before.get(name)) != _canonical(chain_after.get(name))
            ),
        },
        "operations": {
            "added": [item for item in after_operations if item not in before_operations],
            "removed": [item for item in before_operations if item not in after_operations],
            "modified": sorted(
                identifier
                for identifier in before_operations
                if identifier in after_operations
                and _canonical(before_operations[identifier]) != _canonical(after_operations[identifier])
            ),
        },
    }


def _verification_surface_changed(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    return any(
        _canonical(previous.get(field)) != _canonical(current.get(field))
        for field in VERIFICATION_SURFACE_FIELDS
    )


def required_evidence_floor(contract: dict[str, Any]) -> int | None:
    """The task-level evidence floor the lifecycle reads: max(required_evidence_levels)."""
    levels = contract.get("required_evidence_levels") if isinstance(contract, dict) else None
    values = [
        item for item in (levels if isinstance(levels, list) else [])
        if isinstance(item, int) and not isinstance(item, bool)
    ]
    return max(values) if values else None


def _contract_loosened(previous: dict[str, Any], current: dict[str, Any], changes: dict[str, Any]) -> bool:
    """Whether a revision relaxes what the contract requires."""
    tests = changes["acceptance_tests"]
    if tests["removed"]:
        return True
    for item in tests["modified"]:
        for name, delta in item["fields"].items():
            if delta["to"] is None:
                return True
            if name == "evidence_level":
                before, after = delta["from"], delta["to"]
                if isinstance(before, int) and not isinstance(before, bool):
                    if not isinstance(after, int) or isinstance(after, bool) or after < before:
                        return True
            elif name in LOOSENING_ACCEPTANCE_FIELDS:
                return True
    # The task-level floor is the number the lifecycle turns into "ready"; lowering
    # it (by dropping or shrinking the levels) lowers what the task must prove.
    before_floor = required_evidence_floor(previous)
    after_floor = required_evidence_floor(current)
    if before_floor is not None and (after_floor is None or after_floor < before_floor):
        return True
    if changes["allowed_paths"]["added"]:
        return True
    if changes["forbidden_paths"]["removed"]:
        return True
    return bool(changes["non_goals"]["removed"])


def _write_amendments(path: Path, document: dict[str, Any]) -> None:
    """Append-only writer: one record per line, earlier lines never rewritten."""
    records = [json.dumps(record, ensure_ascii=True, sort_keys=True) for record in document["revisions"]]
    text = (
        '{"schema": ' + json.dumps(document["schema"]) + ', "task_id": '
        + json.dumps(document["task_id"], ensure_ascii=True)
        + ', "revisions": [\n' + "\n,\n".join(records) + "\n]}\n"
    )
    _atomic_write_text(path, text)


def amend_task_sheet(
    root: Path,
    task_id: str,
    *,
    reason: str,
    adjudication: str | None = None,
    requested_by: str = "main-agent",
    feedback_ref: str | None = None,
    role: str = AMENDMENT_WRITER_ROLE,
    task_sheet: Path | None = None,
) -> dict[str, Any]:
    """Classify, validate, and record one task sheet revision.

    The tool validates and records only: the main agent edits the task sheet
    first and this call decides whether the change is acceptable.  A rejected
    amendment leaves no record, no hash change and no moved file.
    """

    def outcome(status: str, errors: list[str] | None = None, **extra: Any) -> dict[str, Any]:
        return {
            "schema": 1,
            "command": "task.amend",
            "status": status,
            "exit_code": {"pass": PASS, "fail": FAIL, "config": CONFIG, "blocked": BLOCKED}[status],
            "task_id": task_id,
            "phase": "contract",
            "observed": extra.pop("observed", []),
            "errors": list(errors or []),
            "blockers": extra.pop("blockers", []),
            "artifacts": extra.pop("artifacts", []),
            "next_actions": extra.pop("next_actions", []),
            "unverified": extra.pop("unverified", []),
            **extra,
        }

    root = Path(root)
    if role != AMENDMENT_WRITER_ROLE:
        return outcome(
            "blocked",
            ["role=main-agent is required for task sheet amendments"],
            next_actions=["retry with role=main-agent"],
        )
    if not _safe_task_identifier(task_id):
        return outcome("config", ["invalid task id"])
    if not isinstance(reason, str) or not reason.strip():
        return outcome("config", ["--reason must be a non-empty string"])
    if requested_by not in AMENDMENT_REQUEST_ROLES:
        return outcome("config", [f"--requested-by must be one of {', '.join(AMENDMENT_REQUEST_ROLES)}"])
    for label, reference in (("reason", reason), ("adjudication", adjudication), ("feedback_ref", feedback_ref)):
        if reference is not None and not isinstance(reference, str):
            return outcome("config", [f"--{label} must be a string"])
    sheet = Path(task_sheet) if task_sheet is not None else task_sheet_path(root, task_id)
    if sheet is None or not sheet.is_file():
        return outcome("config", [f"task sheet not found for task id: {task_id}"])
    contract, contract_errors = load_contract(sheet)
    if contract_errors or not isinstance(contract, dict):
        return outcome("config", ["task sheet is not a valid frozen contract", *contract_errors])
    record, record_errors = read_amendments(root, task_id)
    if record_errors:
        return outcome("blocked", record_errors)
    previous, previous_errors = _previous_sheet_contract(root, task_id, sheet)
    if previous is None:
        return outcome(
            "config",
            ["the previous task sheet revision is unavailable; freeze the task sheet before amending", *previous_errors],
        )
    identity_changes = sorted(
        field for field in CONTRACT_IDENTITY_FIELDS if _canonical(previous.get(field)) != _canonical(contract.get(field))
    )
    if identity_changes:
        return outcome(
            "blocked",
            [f"contract field {field} is not amendable (identity field)" for field in identity_changes],
            next_actions=["create a new task instead of re-identifying this one"],
        )
    if contract.get("task_id") != task_id:
        return outcome("blocked", [f"task sheet task_id does not match --task-id: {task_id}"])
    changes = _contract_changes(previous, contract)
    dependencies = [item for item in (_dependency_id(entry) for entry in contract.get("dependencies", [])) if item]
    if changes["dependencies"]["added"] or changes["dependencies"]["removed"]:
        missing = [item for item in dependencies if task_sheet_path(root, item) is None]
        if missing:
            return outcome("blocked", [f"dependency task sheet not found: {item}" for item in missing])
        unresolvable = [item for item in dependencies if _dependency_edges(root, item) is None]
        if unresolvable:
            return outcome("blocked", [f"dependency task sheet is not a valid contract: {item}" for item in unresolvable])
        cycle = dependency_cycle(root, task_id, dependencies)
        if cycle:
            return outcome("blocked", ["dependency cycle: " + " -> ".join(cycle)])
    surface_changed = _verification_surface_changed(previous, contract)
    loosened = _contract_loosened(previous, contract, changes)
    if loosened and not (isinstance(adjudication, str) and adjudication.strip()):
        return outcome(
            "blocked",
            ["loosening the contract requires --adjudication"],
            next_actions=["record the adjudication reference and retry"],
        )
    revision, baseline = task_sheet_revision(root, task_id)
    observed = _file_sha256(sheet)
    if observed is None:
        return outcome("config", ["task sheet unreadable"])
    if observed == baseline:
        return outcome("config", [f"task sheet is unchanged since revision {revision}; nothing to amend"])
    existing = list(record["revisions"]) if record else []
    entry: dict[str, Any] = {
        "revision": revision + 1,
        "at": datetime.now().astimezone().isoformat(),
        "by": AMENDMENT_WRITER_ROLE,
        "requested_by": requested_by,
        "feedback_ref": feedback_ref or None,
        "reason": reason.strip(),
        "adjudication_ref": adjudication.strip() if isinstance(adjudication, str) and adjudication.strip() else None,
        "previous_sheet_sha256": baseline,
        "sheet_sha256": observed,
        "verification_surface_changed": surface_changed,
        "loosened": loosened,
        "changes": changes,
        "sheet_contract": contract,
    }
    path = amendments_path(root, task_id)
    try:
        _write_amendments(path, {"schema": AMENDMENT_SCHEMA, "task_id": task_id, "revisions": [*existing, entry]})
    except OSError as error:
        return outcome("blocked", [f"amendment record could not be written: {type(error).__name__}"])
    next_actions = ["commit the amended task sheet"]
    if surface_changed:
        next_actions.append("redo the affected stage evidence against the new revision")
    return outcome(
        "pass",
        revision=entry["revision"],
        previous_revision=revision,
        verification_surface_changed=surface_changed,
        loosened=loosened,
        requested_by=requested_by,
        feedback_ref=entry["feedback_ref"],
        adjudication_ref=entry["adjudication_ref"],
        previous_sheet_sha256=baseline,
        sheet_sha256=observed,
        changes=changes,
        observed=[
            {"fact": "task_sheet_revision", "value": entry["revision"]},
            {"fact": "verification_surface_changed", "value": surface_changed},
            {"fact": "loosened", "value": loosened},
        ],
        artifacts=[str(path)],
        next_actions=next_actions,
    )


def _evidence_acceptance_ids(value: Any) -> set[str]:
    if not isinstance(value, dict):
        return set()
    acceptance = value.get("acceptance")
    if not isinstance(acceptance, list):
        return set()
    return {
        item["id"]
        for item in acceptance
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _operation_resource_paths(contract: dict[str, Any]) -> list[tuple[set[str], list[str]]]:
    operations = contract.get("operations") if isinstance(contract, dict) else None
    entries: list[tuple[set[str], list[str]]] = []
    for operation in operations if isinstance(operations, list) else []:
        if not isinstance(operation, dict):
            continue
        tests = operation.get("acceptance_tests")
        entries.append((
            {item for item in tests if isinstance(item, str)} if isinstance(tests, list) else set(),
            _string_list(operation.get("resources")),
        ))
    return entries


def sheet_operation_resources(contract: dict[str, Any], acceptance_ids: set[str]) -> list[str]:
    """Resources of the operations that own the given acceptance tests.

    Evidence that declares no acceptance ids speaks for the whole task, so it is
    measured against every operation resource.
    """
    entries = _operation_resource_paths(contract)
    owned = sorted({resource for tests, resources in entries if tests & acceptance_ids for resource in resources})
    if owned:
        return owned
    return sorted({resource for _tests, resources in entries for resource in resources})


def changed_paths_between(root: Path, base: str, head: str | None = None) -> list[str] | None:
    """Return paths changed from a recorded commit to HEAD, or None if unknown."""
    if not isinstance(base, str) or not base.strip():
        return None
    rc, _ = git(root, "rev-parse", "--verify", f"{base.strip()}^{{commit}}")
    if rc:
        return None
    rc, output = git(root, "diff", "--name-only", base.strip(), head or "HEAD", redact_output=False)
    if rc:
        return None
    return [path.replace("\\", "/") for path in output.splitlines() if path.strip()]


def evidence_only_paths(root: Path, evidence_directory: Path, changed_paths: list[str]) -> bool:
    """Whether every changed path belongs to this task's own evidence.

    Committing the task's evidence tree (and the metrics stream) is workflow
    bookkeeping: it advances HEAD without changing the product or the tests, so
    it must never invalidate evidence.  This is the single basis shared by
    ``evidence_freshness`` and the schema-2 report head check.
    """
    try:
        evidence_root = Path(evidence_directory).resolve().relative_to(Path(root).resolve()).as_posix()
    except (OSError, ValueError):
        return False
    if not evidence_root:
        return False
    return all(
        path == evidence_root
        or path.startswith(evidence_root + "/")
        or is_metrics_path(path)
        for path in changed_paths
    )


def head_advanced_by_evidence_only(
    root: Path,
    reported_head: Any,
    current_head: Any,
    evidence_directory: Path,
) -> bool:
    """Whether HEAD moved past ``reported_head`` by committing only task evidence.

    A record names the commit it judged.  Publishing that record moves HEAD, so
    requiring exact equality would make every report invalidate itself.  Only a
    plain commit range whose changed paths are all this task's evidence (or the
    metrics stream) is accepted; an unknown, non-ancestor or product-touching
    range keeps the strict rule.
    """
    if not isinstance(reported_head, str) or not isinstance(current_head, str):
        return False
    if reported_head == current_head:
        return True
    if not re.fullmatch(r"[0-9a-fA-F]{40}", reported_head):
        return False
    rc, _ = git(root, "merge-base", "--is-ancestor", reported_head, current_head)
    if rc:
        return False
    changed = changed_paths_between(root, reported_head, current_head)
    if changed is None:
        return False
    return evidence_only_paths(root, evidence_directory, changed)


def evidence_revision_status(
    root: Path,
    task_id: str,
    contract: dict[str, Any],
    records: dict[str, dict[str, Any]],
    *,
    judge_observed_paths: bool = True,
) -> dict[str, Any]:
    """Judge evidence against the sheet revision it was produced for.

    Evidence is stale when the revision it names is not the current revision, or
    when a path its operations verify changed between the commit it was observed
    at and HEAD.  HEAD moving on its own never invalidates evidence.

    ``judge_observed_paths`` selects whether that second, commit-relative
    criterion applies.  The post-merge phase passes it as False: merging always
    moves HEAD past the recorded observation commit, so the identity there is the
    task id plus the revision and the observation commit stays a recorded fact.

    Only evidence that declares ``sheet_revision`` is judged this way.  Evidence
    in the historical shape (no revision field) keeps exactly the verdict the
    older rules gave it, so a missing new field never adds an error by itself;
    it is reported as unverified instead.
    """
    root = Path(root)
    revision, baseline = task_sheet_revision(root, task_id)
    rc, head = git(root, "rev-parse", "HEAD")
    current_head = head.strip() if rc == 0 else None
    details: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    unverified: list[str] = []
    for name in sorted(records):
        value = records[name]
        reasons: list[str] = []
        declared = value.get("sheet_revision")
        declared_hash = value.get("sheet_sha256")
        observed_at = value.get("observed_at_commit")
        bound = isinstance(declared, int) and not isinstance(declared, bool)
        judged = False
        if bound:
            if declared != revision:
                reasons.append(
                    f"{name} was produced against task sheet revision {declared} "
                    f"but the current revision is {revision}"
                )
            elif baseline is not None and declared_hash != baseline:
                reasons.append(f"{name} task sheet hash does not match revision {revision}")
            if judge_observed_paths:
                if not isinstance(observed_at, str) or not observed_at.strip():
                    unverified.append(
                        f"{name} does not record the commit it was observed at; "
                        "the changed-path criterion was not evaluated"
                    )
                elif current_head is None:
                    unverified.append(
                        f"{name} declares an observation commit but HEAD is unavailable; "
                        "the changed-path criterion was not evaluated"
                    )
                else:
                    changed = changed_paths_between(root, observed_at.strip(), current_head)
                    if changed is None:
                        reasons.append(f"{name} observed_at_commit is not a reachable commit: {observed_at.strip()}")
                    else:
                        judged = True
                        resources = sheet_operation_resources(contract, _evidence_acceptance_ids(value))
                        touched = sorted({path for path in changed if any(_matches(path, pattern, root) for pattern in resources)})
                        if touched:
                            reasons.append(
                                f"{name} was produced before changes to paths it verifies: " + ", ".join(touched)
                            )
        else:
            unverified.append(
                f"{name} does not record the task sheet revision it was judged against; "
                "the revision criteria were not applied"
            )
        details[name] = {
            "sheet_revision": declared if bound else None,
            "sheet_sha256": declared_hash if isinstance(declared_hash, str) else None,
            "observed_at_commit": observed_at if isinstance(observed_at, str) else None,
            "revision_bound": bound,
            "changed_paths_judged": judged,
            "stale": bool(reasons),
            "reasons": reasons,
        }
        errors.extend(reasons)
    return {
        "schema": 1,
        "sheet_revision": revision,
        "sheet_sha256": baseline,
        "head": current_head,
        "records": details,
        "stale": bool(errors),
        "errors": errors,
        "unverified": unverified,
    }


# Backwards-compatible name used by the first CLI draft.
def freeze_check(
    root: Path,
    contract: str,
    expected_head: str | None = None,
    expected_branch: str | None = None,
    expected_worktree: Path | None = None,
    task_sheet: Path | None = None,
    *,
    unverified: list[str] | None = None,
) -> list[str]:
    """Verify contract ancestry, optional identity, and implement-plan hash stability."""
    errors: list[str] = []
    rc, _ = git(root, "rev-parse", "--verify", "HEAD")
    if rc:
        return ["not a git repository"]
    rc, _ = git(root, "cat-file", "-e", f"{contract}^{{commit}}")
    if rc:
        return ["contract commit unavailable"]
    rc, _ = git(root, "merge-base", "--is-ancestor", contract, "HEAD")
    if rc:
        errors.append("contract commit is not an ancestor")
    if expected_head:
        rc, actual = git(root, "rev-parse", "HEAD")
        if rc or actual.strip() != expected_head:
            errors.append("HEAD does not match expected head")
    if expected_branch:
        rc, actual = git(root, "branch", "--show-current")
        if rc or actual.strip() != expected_branch:
            errors.append("branch does not match expected branch")
    if expected_worktree:
        rc, actual = git(
            root,
            "rev-parse",
            "--show-toplevel",
            redact_output=False,
        )
        try:
            expected = expected_worktree.resolve()
            actual_path = Path(actual.strip()).resolve()
        except (OSError, ValueError):
            errors.append("worktree identity cannot be resolved")
        else:
            if rc or actual_path != expected:
                errors.append("worktree does not match expected worktree")
    if task_sheet is not None:
        task_sheet = Path(task_sheet)
        sheet_contract, sheet_errors = load_contract(task_sheet)
        if sheet_contract is None or sheet_errors:
            errors.append("task sheet is not a valid frozen contract")
        else:
            sheet_task_id = sheet_contract.get("task_id")
            amendments_invalid = read_amendments(root, sheet_task_id)[1] if isinstance(sheet_task_id, str) else []
            recorded_sheet = task_sheet_baseline_sha256(root, sheet_task_id)
            observed_sheet = _file_sha256(task_sheet)
            if amendments_invalid:
                errors.extend(f"task sheet amendment record is invalid: {item}" for item in amendments_invalid)
            if recorded_sheet and observed_sheet and recorded_sheet != observed_sheet:
                errors.append("task sheet changed after freeze")
            if sheet_contract.get("task_type") == "derived":
                derived_from = sheet_contract.get("derived_from")
                if isinstance(derived_from, dict):
                    parent_id = derived_from.get("task_id")
                    parent_commit = derived_from.get("commit")
                    declared_parent_type = derived_from.get("parent_task_type")
                    if isinstance(parent_id, str) and isinstance(parent_commit, str):
                        rc, parent_text = git(root, "show", f"{parent_commit}:docs/tasks/{parent_id}.md", redact_output=False)
                        if rc:
                            errors.append("derived task parent sheet is unavailable at the declared commit")
                        else:
                            parent_contract = _contract_from_text(parent_text)
                            if not isinstance(parent_contract, dict):
                                errors.append("derived task parent sheet has no readable contract")
                            elif parent_contract.get("task_type") != declared_parent_type:
                                errors.append("derived_from.parent_task_type does not match the parent task sheet")
            plan_errors, _recorded_hash, observed_hash, plan_unverified = implement_plan_status(
                root, sheet_contract, sheet_task_id
            )
            _record_goal_hash(
                root, sheet_task_id, observed_hash, observed_sheet,
                legacy=sheet_contract.get("schema") != 4,
                task_sheet_contract=sheet_contract,
            )
            if unverified is not None:
                unverified.extend(plan_unverified)
            errors.extend(plan_errors)
    return errors
