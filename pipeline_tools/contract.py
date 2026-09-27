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
SUPPORTED_SCHEMAS = {1, 2, 3}
CHAIN_NAMES = ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")
TASK_TYPES = {"vertical-feature", "prerequisite", "repair", "derived"}
PROJECT_TYPES = ("library", "cli", "service", "web", "desktop", "multi-process")
DEFAULT_PROJECT_TYPE = "service"
RISK_LEVELS = ("low", "medium", "high")
OPERATION_RESOURCE_MODES = ("single", "batch")
NOT_APPLICABLE_LITERAL = "not-applicable"
# Evidence floor table. These numbers are the single source of truth for the
# schema-3 gate, for planning.py and for the documentation.
EVIDENCE_FLOOR_BY_RISK = {"low": 1, "medium": 2, "high": 3}
EVIDENCE_FLOOR_BY_PROJECT_TYPE = {"web": 3, "desktop": 3, "multi-process": 4}
VERTICAL_FEATURE_EVIDENCE_FLOOR = 2


def _nonempty_array(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _safe_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(IDENTIFIER_RE.fullmatch(value))


def _validate_full_acceptance_id(value: Any) -> bool:
    return isinstance(value, str) and bool(ACCEPTANCE_ID_RE.fullmatch(value))


def _validate_chain(
    value: Any,
    errors: list[str],
    label: str = "chain",
    allow_not_applicable: bool = False,
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    for name in CHAIN_NAMES:
        entries = value.get(name)
        if allow_not_applicable and isinstance(entries, dict):
            if entries.get("not_applicable") is True and _nonempty_string(entries.get("reason")):
                continue
            errors.append(f"{label}.{name} not_applicable requires a non-empty reason")
        elif not isinstance(entries, list) or not entries:
            errors.append(f"{label}.{name} must be a non-empty array")
        elif any(not _nonempty_string(item) and not isinstance(item, dict) for item in entries):
            errors.append(f"{label}.{name} contains an invalid reference")


def _validate_schema2_contract(
    data: dict[str, Any],
    errors: list[str],
    allow_not_applicable_chain: bool = False,
) -> None:
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
    _validate_chain(data.get("chain"), errors, allow_not_applicable=allow_not_applicable_chain)
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


def evidence_floor(
    risk: Any,
    project_type: Any,
    task_type: Any,
    parent_task_type: str | None = None,
) -> int | None:
    """Return the minimum evidence level for a schema-3 task, or None if inputs are invalid."""
    if risk not in EVIDENCE_FLOOR_BY_RISK:
        return None
    floor = EVIDENCE_FLOOR_BY_RISK[risk]
    if risk != "low" and project_type in EVIDENCE_FLOOR_BY_PROJECT_TYPE:
        floor = max(floor, EVIDENCE_FLOOR_BY_PROJECT_TYPE[project_type])
    if task_type == "vertical-feature" or parent_task_type == "vertical-feature":
        floor = max(floor, VERTICAL_FEATURE_EVIDENCE_FLOOR)
    return floor


def _validate_derived_from(data: dict[str, Any], errors: list[str]) -> None:
    derived_from = data.get("derived_from")
    if not isinstance(derived_from, dict):
        errors.append("derived task requires a derived_from object")
        return
    for field in ("task_id", "commit", "branch"):
        if not _nonempty_string(derived_from.get(field)):
            errors.append(f"derived_from.{field} is required")
    parent_task_type = derived_from.get("parent_task_type")
    if not _nonempty_string(parent_task_type):
        errors.append("derived_from.parent_task_type is required")
    elif parent_task_type not in TASK_TYPES:
        errors.append(
            "derived_from.parent_task_type must be one of "
            + ", ".join(sorted(TASK_TYPES))
        )


def _requires_full_chain(data: dict[str, Any]) -> bool:
    """Whether the task's chain must carry real references instead of not_applicable."""
    task_type = data.get("task_type")
    if task_type in {"vertical-feature", "repair"}:
        return True
    if task_type == "derived":
        derived_from = data.get("derived_from")
        parent_task_type = (
            derived_from.get("parent_task_type")
            if isinstance(derived_from, dict)
            else None
        )
        return parent_task_type in {"vertical-feature", "repair"}
    return False


def _validate_schema3_contract(data: dict[str, Any], errors: list[str]) -> None:
    non_goals = data.get("non_goals")
    if not isinstance(non_goals, list) or not non_goals:
        errors.append("non_goals must be a non-empty array")
    elif any(not _nonempty_string(item) for item in non_goals):
        errors.append("non_goals must contain only non-empty strings")

    risk = data.get("risk")
    if risk not in RISK_LEVELS:
        errors.append("risk must be one of low, medium, high")

    project_type = data.get("project_type", DEFAULT_PROJECT_TYPE)
    if project_type not in PROJECT_TYPES:
        errors.append("project_type must be one of " + ", ".join(PROJECT_TYPES))
        project_type = DEFAULT_PROJECT_TYPE

    task_type = data.get("task_type")

    for name in CHAIN_NAMES:
        entries = (data.get("chain") or {}).get(name) if isinstance(data.get("chain"), dict) else None
        if isinstance(entries, list) and any(item == NOT_APPLICABLE_LITERAL for item in entries):
            errors.append(
                f"chain.{name} must not use the literal \"{NOT_APPLICABLE_LITERAL}\"; "
                "use {\"not_applicable\": true, \"reason\": \"...\"}"
            )

    operations = data.get("operations")
    if isinstance(operations, list):
        for index, operation in enumerate(operations, 1):
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("id") if _safe_identifier(operation.get("id")) else f"#{index}"
            resources = operation.get("resources")
            mode = operation.get("resource_mode")
            if not isinstance(resources, list) or not resources:
                errors.append(f"operation {operation_id} must declare non-empty resources")
                continue
            if mode not in OPERATION_RESOURCE_MODES:
                errors.append(f"operation {operation_id} resource_mode must be one of single, batch")
                continue
            expected = "single" if len(resources) == 1 else "batch"
            if mode != expected:
                errors.append(
                    f"operation {operation_id} resource_mode {mode} does not match "
                    f"{len(resources)} resource(s); expected {expected}"
                )

    for field in ("assumptions", "unknowns"):
        records = data.get(field, [])
        if not isinstance(records, list):
            errors.append(f"{field} must be an array")
            continue
        for index, record in enumerate(records, 1):
            if not isinstance(record, dict):
                errors.append(f"{field}[{index}] must be an object")
                continue
            identifier = record.get("id")
            if identifier is not None and not _safe_identifier(identifier):
                errors.append(f"{field}[{index}] id must be a safe identifier")

    if task_type == "prerequisite" and not _nonempty_string(data.get("non_user_completion_reason")):
        errors.append("prerequisite task requires a non-empty non_user_completion_reason")

    if task_type == "derived":
        _validate_derived_from(data, errors)

    parent_task_type = None
    if task_type == "derived":
        derived_from = data.get("derived_from")
        if isinstance(derived_from, dict):
            parent_task_type = derived_from.get("parent_task_type")

    floor = evidence_floor(risk, project_type, task_type, parent_task_type)
    if floor is not None:
        for index, item in enumerate(data.get("acceptance_tests", []), 1):
            if not isinstance(item, dict):
                continue
            level = item.get("evidence_level")
            if isinstance(level, bool) or not isinstance(level, int):
                continue
            if level < floor:
                errors.append(
                    f"acceptance test {item.get('id', index)} evidence_level {level} "
                    f"is below the required floor {floor}"
                )


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
        errors.append("schema must be integer 1, 2 or 3")

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
        id_valid = (
            _validate_full_acceptance_id(test_id)
            if schema in {2, 3}
            else isinstance(test_id, str) and bool(IDENTIFIER_RE.fullmatch(test_id))
        )
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

    if schema in {2, 3}:
        allow_not_applicable_chain = schema == 3 and not _requires_full_chain(data)
        _validate_schema2_contract(
            data, errors, allow_not_applicable_chain=allow_not_applicable_chain
        )
    if schema == 3:
        _validate_schema3_contract(data, errors)

    return (data if not errors else None), errors


def validate_task(path: Path) -> list[str]:
    """Return structural contract errors; never decide product semantics."""
    _data, errors = load_contract(path)
    return errors
