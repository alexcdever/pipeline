"""Machine-readable task contract validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

CONTRACT_RE = re.compile(
    r"```pipeline-contract[ \t]*\r?\n(.*?)\r?\n```", re.DOTALL
)
TASK_ID_RE = re.compile(
    r"<!--\s*Task ID:\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*-->",
    re.IGNORECASE,
)
REQUIRED_FIELDS = (
    "schema",
    "task_id",
    "allowed_paths",
    "forbidden_paths",
    "acceptance_tests",
)
ACCEPTANCE_FIELDS = ("id", "evidence_level", "test_ref", "command_ref")
IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
ACCEPTANCE_ID_RE = re.compile(r"acceptance-test-[A-Za-z0-9][A-Za-z0-9._-]*\Z")
SUPPORTED_SCHEMAS = {1, 2}
CHAIN_NAMES = ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")
TASK_TYPES = {"vertical-feature", "prerequisite", "repair", "derived"}


def _nonempty_array(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _safe_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(IDENTIFIER_RE.fullmatch(value))


def _validate_full_acceptance_id(value: Any) -> bool:
    return isinstance(value, str) and bool(ACCEPTANCE_ID_RE.fullmatch(value))


def _validate_chain(value: Any, errors: list[str], label: str = "chain") -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    for name in CHAIN_NAMES:
        entries = value.get(name)
        if not isinstance(entries, list) or not entries:
            errors.append(f"{label}.{name} must be a non-empty array")
        elif any(not _nonempty_string(item) and not isinstance(item, dict) for item in entries):
            errors.append(f"{label}.{name} contains an invalid reference")


def _validate_schema2_contract(data: dict[str, Any], errors: list[str]) -> None:
    if not _nonempty_string(data.get("task_type")) or data.get("task_type") not in TASK_TYPES:
        errors.append("task_type must be one of vertical-feature, prerequisite, repair, derived")
    implement_plan = data.get("implement_plan")
    if not isinstance(implement_plan, dict) or not _nonempty_string(implement_plan.get("path")):
        errors.append("implement_plan.path is required")
    operations = data.get("operations")
    operation_ids: set[str] = set()
    operation_acceptance_refs: dict[str, list[str]] = {}
    if not _nonempty_array(operations):
        errors.append("operations must be a non-empty array")
        operations = []
    for index, operation in enumerate(operations, 1):
        if not isinstance(operation, dict) or not _safe_identifier(operation.get("id")):
            errors.append(f"operation {index} must contain a safe id")
            continue
        operation_id = operation["id"]
        if operation_id in operation_ids:
            errors.append(f"duplicate operation id: {operation_id}")
        operation_ids.add(operation_id)
        for field in ("kind", "scope"):
            if not _nonempty_string(operation.get(field)):
                errors.append(f"operation {operation_id} missing field: {field}")
        tests = operation.get("acceptance_tests")
        if not _nonempty_array(tests):
            errors.append(f"operation {operation_id} must declare acceptance_tests")
        else:
            operation_acceptance_refs[operation_id] = list(tests)
            for test_id in tests:
                if not _validate_full_acceptance_id(test_id):
                    errors.append(f"operation {operation_id} acceptance_tests must use full names")
    acceptance_ids = {
        item.get("id") for item in data.get("acceptance_tests", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for operation_id, refs in operation_acceptance_refs.items():
        for ref in refs:
            if ref not in acceptance_ids:
                errors.append(f"operation {operation_id} references unknown acceptance test: {ref}")
    _validate_chain(data.get("chain"), errors)
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, list):
        errors.append("dependencies must be an array")
    else:
        for dependency in dependencies:
            if not isinstance(dependency, (str, dict)):
                errors.append("dependencies contain an invalid entry")
    levels = data.get("required_evidence_levels")
    if not isinstance(levels, list) or any(isinstance(level, bool) or not isinstance(level, int) or not 1 <= level <= 5 for level in levels):
        errors.append("required_evidence_levels must contain integers 1-5")



def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_path_pattern(value: Any) -> bool:
    """Accept repo-relative patterns and explicit absolute allow-list patterns."""
    if not _nonempty_string(value) or "\x00" in value:
        return False
    normalized = value.replace("\\", "/")
    if "<" in normalized or ">" in normalized:
        return False
    # Absolute patterns are useful when one task spans sibling repositories.
    # Traversal segments are never allowed.
    segments = normalized.split("/")
    return ".." not in segments


def load_contract(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Load and validate the JSON contract block without inferring missing data."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None, ["task sheet unreadable"]

    blocks = CONTRACT_RE.findall(text)
    if len(blocks) != 1:
        return None, ["task sheet must contain exactly one pipeline-contract block"]

    try:
        data = json.loads(blocks[0])
    except json.JSONDecodeError as exc:
        return None, [f"pipeline-contract JSON is invalid at line {exc.lineno}"]
    if not isinstance(data, dict):
        return None, ["pipeline-contract must be a JSON object"]

    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing contract field: {field}")

    task_match = TASK_ID_RE.search(text)
    if not task_match:
        errors.append("missing valid Task ID")
    elif data.get("task_id") != task_match.group(1):
        errors.append("task_id does not match Task ID")

    schema = data.get("schema")
    if isinstance(schema, bool) or schema not in SUPPORTED_SCHEMAS:
        errors.append("schema must be integer 1 or 2")

    for field in ("allowed_paths", "forbidden_paths"):
        values = data.get(field)
        if not isinstance(values, list):
            errors.append(f"{field} must be an array")
            continue
        for index, value in enumerate(values, start=1):
            if not _valid_path_pattern(value):
                errors.append(
                    f"{field}[{index}] must be a non-empty safe path pattern"
                )

    tests = data.get("acceptance_tests")
    if not isinstance(tests, list) or not tests:
        errors.append("acceptance_tests must be a non-empty array")
        tests = []

    seen_ids: set[str] = set()
    for index, item in enumerate(tests, start=1):
        if not isinstance(item, dict):
            errors.append(f"acceptance test {index} must be an object")
            continue
        for field in ACCEPTANCE_FIELDS:
            if field not in item:
                errors.append(f"acceptance test {index} missing field: {field}")

        test_id = item.get("id")
        id_valid = _validate_full_acceptance_id(test_id) if schema == 2 else isinstance(test_id, str) and bool(IDENTIFIER_RE.fullmatch(test_id))
        if not id_valid:
            errors.append(f"acceptance test {index} has invalid id")
        elif test_id in seen_ids:
            errors.append(f"duplicate acceptance test id: {test_id}")
        else:
            seen_ids.add(test_id)

        for field in ("test_ref", "command_ref"):
            value = item.get(field)
            if not _nonempty_string(value) or "<" in value or ">" in value:
                errors.append(
                    f"acceptance test {index} has empty or placeholder {field}"
                )

        level = item.get("evidence_level")
        if isinstance(level, bool) or not isinstance(level, int) or not 1 <= level <= 5:
            errors.append(f"acceptance test {index} evidence_level must be integer 1-5")

    if schema == 2:
        _validate_schema2_contract(data, errors)

    return (data if not errors else None), errors


def validate_task(path: Path) -> list[str]:
    """Return structural contract errors; never decide product semantics."""
    _data, errors = load_contract(path)
    return errors
