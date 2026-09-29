"""Project-local storage layout and migration compatibility helpers."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path


TEMP_DIR_NAME = "pipeline-tools"
RECOVERY_INDEX_NAME = "recovery-index.json"

PIPELINE_DIR_NAME = ".pipeline"
LEGACY_PIPELINE_DIR_NAME = ".workflow"
PIPELINE_DIR_NAMES = (PIPELINE_DIR_NAME,)
LAYOUT_DIR_NAMES = (PIPELINE_DIR_NAME, LEGACY_PIPELINE_DIR_NAME)


class LegacyPipelineLayoutError(ValueError):
    """Raised when legacy and canonical evidence directories conflict."""


def temporary_root(root: Path | None = None) -> Path:
    """Return the shared system temporary directory for transient artifacts."""
    identity_source = Path(root).resolve() if root is not None else Path.cwd().resolve()
    identity = hashlib.sha256(str(identity_source).encode("utf-8")).hexdigest()[:12]
    path = Path(tempfile.gettempdir()) / TEMP_DIR_NAME / identity
    path.mkdir(parents=True, exist_ok=True)
    return path


def temporary_path(name: str | None = None, *, suffix: str = "", root: Path | None = None) -> Path:
    """Allocate a transient path without allowing callers to escape its root."""
    root = temporary_root(root).resolve()
    if name is None:
        return Path(tempfile.mkstemp(prefix="run-", suffix=suffix, dir=root)[1])
    candidate = (root / name).resolve()
    if candidate.parent != root or candidate == root:
        raise ValueError("temporary path must be a direct child of the shared temporary root")
    return candidate


def temporary_log_path(name: str | None = None, *, root: Path | None = None) -> Path:
    """Return a shared transient log path, preserving explicit names for compatibility."""
    if name is None:
        return temporary_path(suffix=".log", root=root)
    path = Path(name)
    if path.is_absolute():
        return path
    return temporary_path(name, root=root)


def recovery_index_path(root: Path) -> Path:
    """Return the canonical, project-relative index used to recover retained failures."""
    return active_pipeline_dir(Path(root)) / RECOVERY_INDEX_NAME


def migrate_layout(root: Path) -> tuple[int, str]:
    """Move a legacy .workflow tree to .pipeline without overwriting files."""
    import hashlib
    import os
    import shutil

    legacy = root / LEGACY_PIPELINE_DIR_NAME
    canonical = root / PIPELINE_DIR_NAME
    if not legacy.exists():
        return 0, "absent"
    if canonical.exists():
        raise LegacyPipelineLayoutError("both .workflow and .pipeline exist; reconcile before migration")

    def manifest(directory: Path) -> dict[str, tuple[int, str]]:
        return {
            path.relative_to(directory).as_posix(): (
                path.stat().st_size,
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
            for path in directory.rglob("*")
            if path.is_file()
        }

    before = manifest(legacy)
    try:
        os.rename(legacy, canonical)
    except OSError:
        # A rename across filesystems (or a locked directory) is retried as a
        # copy-and-delete move; the manifest comparison below still proves the
        # contents survived and no canonical tree was overwritten.
        if canonical.exists():
            raise LegacyPipelineLayoutError("both .workflow and .pipeline exist; reconcile before migration")
        try:
            shutil.move(str(legacy), str(canonical))
        except OSError as error:
            raise LegacyPipelineLayoutError(f"migration failed: {error}") from error
    after = manifest(canonical)
    if before != after:
        raise LegacyPipelineLayoutError("migration changed file contents")
    return len(before), "migrated"


def active_pipeline_dir(root: Path) -> Path:
    """Automatically migrate legacy evidence before returning the canonical path."""
    legacy = root / LEGACY_PIPELINE_DIR_NAME
    canonical = root / PIPELINE_DIR_NAME
    if legacy.exists():
        migrate_layout(root)
    return canonical


def read_pipeline_dirs(root: Path) -> list[Path]:
    """Return readable canonical/legacy roots without changing the filesystem."""
    root = Path(root)
    canonical = root / PIPELINE_DIR_NAME
    legacy = root / LEGACY_PIPELINE_DIR_NAME
    if canonical.exists() and legacy.exists():
        raise LegacyPipelineLayoutError("both .workflow and .pipeline exist; reconcile before migration")
    return [canonical] if canonical.exists() else [legacy]


def metrics_dirs(root: Path) -> list[Path]:
    """Return the canonical metrics directory after automatic migration."""
    return [active_pipeline_dir(root) / "metrics"]


def canonical_evidence_dir(directory: Path) -> Path:
    """Return the canonical task directory, migrating a legacy parent first."""
    if directory.parent.name not in LAYOUT_DIR_NAMES:
        return directory
    root = directory.parent.parent
    active_pipeline_dir(root)
    return root / PIPELINE_DIR_NAME / directory.name


def is_metrics_path(path: str) -> bool:
    """Return whether a normalized project-relative path is pipeline metrics."""
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return any(
        normalized == f"{name}/metrics" or normalized.startswith(f"{name}/metrics/")
        for name in PIPELINE_DIR_NAMES
    )


def evidence_root(directory: Path) -> Path:
    """Find the project root for the canonical evidence layout."""
    if directory.parent.name in LAYOUT_DIR_NAMES:
        return directory.parent.parent
    return directory


def layout_parts(path: Path) -> tuple[str, ...]:
    """Return the supported layout components found in a path."""
    return tuple(part for part in path.parts if part in PIPELINE_DIR_NAMES)
