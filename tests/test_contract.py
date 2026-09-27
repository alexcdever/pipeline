import copy
import json
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.contract import validate_task

VALID = '''# T
<!-- Task ID: demo -->
```pipeline-contract
{"schema":1,"task_id":"demo","allowed_paths":["src/**"],"forbidden_paths":["*.secret"],"acceptance_tests":[{"id":"AT1","evidence_level":1,"test_ref":"tests/x.py","command_ref":"python -m unittest"}]}
```
'''

SCHEMA2_VALID = '''# Task
<!-- Task ID: demo -->
```pipeline-contract
{"schema":2,"task_id":"demo","task_type":"repair","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["src/**"],"forbidden_paths":[],"operations":[{"id":"op","kind":"validate","scope":"project","acceptance_tests":["acceptance-test-1"]}],"chain":{"entry":["cli.py"],"interaction":["cli.py"],"application":["app.py"],"domain":["domain.py"],"persistence":["db.py"],"readback":["app.py"],"recovery":["app.py"]},"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":1,"test_ref":"tests/test_x.py: test_x","command_ref":"python -m unittest tests.test_x"}],"dependencies":[],"required_evidence_levels":[1]}
```
'''

CHAIN_NAMES = ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")

SCHEMA3_VALID_DATA = {
    "schema": 3,
    "task_id": "demo",
    "task_type": "repair",
    "project_type": "service",
    "risk": "medium",
    "implement_plan": {"path": "implement-plan.md"},
    "allowed_paths": ["src/**"],
    "forbidden_paths": [],
    "non_goals": ["must not rewrite task history"],
    "operations": [
        {
            "id": "op",
            "kind": "validate",
            "scope": "project",
            "resources": ["src/app.py"],
            "resource_mode": "single",
            "acceptance_tests": ["acceptance-test-1"],
        }
    ],
    "chain": {name: ["src/app.py"] for name in CHAIN_NAMES},
    "acceptance_tests": [
        {
            "id": "acceptance-test-1",
            "evidence_level": 2,
            "test_ref": "tests/test_x.py: test_x",
            "command_ref": "python -m unittest tests.test_x",
        }
    ],
    "dependencies": [],
    "required_evidence_levels": [2],
}


def schema3_sheet(mutate=None):
    data = copy.deepcopy(SCHEMA3_VALID_DATA)
    if mutate is not None:
        mutate(data)
    return "# Task\n<!-- Task ID: demo -->\n```pipeline-contract\n" + json.dumps(data) + "\n```\n"


class ContractTests(unittest.TestCase):
    def test_valid_pipeline_contract(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'task.md'
            path.write_text(VALID, encoding='utf-8')
            self.assertEqual(validate_task(path), [])

    def test_schema2_planning_contract_is_valid(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'task.md'
            path.write_text(SCHEMA2_VALID, encoding='utf-8')
            self.assertEqual(validate_task(path), [])

    def test_schema2_operation_must_bind_complete_acceptance_test(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'task.md'
            path.write_text(SCHEMA2_VALID.replace('acceptance-test-1', 'AT1'), encoding='utf-8')
            errors = validate_task(path)
            self.assertTrue(any('acceptance' in error for error in errors))

            path.write_text(SCHEMA2_VALID.replace('acceptance-test-1', 'acceptance-test-2', 1), encoding='utf-8')
            errors = validate_task(path)
            self.assertTrue(any('unknown acceptance test' in error for error in errors))

    def test_missing_and_bad_contract_fail_without_path(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'private.md'
            path.write_text('# T\n<!-- Task ID: demo -->\n```pipeline-contract\n{}\n```', encoding='utf-8')
            errors = validate_task(path)
            self.assertTrue(errors)
            self.assertNotIn(str(path), ' '.join(errors))

    def test_placeholder_and_duplicate_ids_fail(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 't.md'
            path.write_text(VALID.replace('"AT1"', '"<AT>"'), encoding='utf-8')
            errors = validate_task(path)
            self.assertTrue(any('placeholder' in error or 'id' in error for error in errors))

    def _errors(self, mutate):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'task.md'
            path.write_text(schema3_sheet(mutate), encoding='utf-8')
            return validate_task(path)

    def test_schema3_valid_contract_passes(self):
        self.assertEqual(self._errors(None), [])

    def test_schema3_rejects_missing_or_empty_non_goals(self):
        errors = self._errors(lambda data: data.pop('non_goals'))
        self.assertTrue(any('non_goals' in error for error in errors), errors)
        errors = self._errors(lambda data: data.__setitem__('non_goals', []))
        self.assertTrue(any('non_goals' in error for error in errors), errors)

    def test_schema3_rejects_missing_or_invalid_risk(self):
        errors = self._errors(lambda data: data.pop('risk'))
        self.assertTrue(any('risk' in error for error in errors), errors)
        errors = self._errors(lambda data: data.__setitem__('risk', 'extreme'))
        self.assertTrue(any('risk' in error for error in errors), errors)

    def test_schema3_project_type_defaults_to_service_and_validates_values(self):
        self.assertEqual(self._errors(lambda data: data.pop('project_type')), [])
        errors = self._errors(lambda data: data.__setitem__('project_type', 'embedded'))
        self.assertTrue(any('project_type' in error for error in errors), errors)

    def test_schema3_rejects_not_applicable_chain_literal(self):
        def mutate(data):
            for name in CHAIN_NAMES:
                data['chain'][name] = ['not-applicable']

        errors = self._errors(mutate)
        self.assertTrue(any('not-applicable' in error for error in errors), errors)

        def structured(data):
            data['task_type'] = 'prerequisite'
            data['non_user_completion_reason'] = 'internal groundwork; no user-facing outcome'
            for name in CHAIN_NAMES:
                data['chain'][name] = {'not_applicable': True, 'reason': 'not part of this task'}

        self.assertEqual(self._errors(structured), [])

    def test_schema3_vertical_feature_rejects_all_not_applicable_chain(self):
        def mutate(data):
            data['task_type'] = 'vertical-feature'
            for name in CHAIN_NAMES:
                data['chain'][name] = {'not_applicable': True, 'reason': 'x'}

        errors = self._errors(mutate)
        self.assertTrue(errors, errors)
        self.assertTrue(
            any('must be a non-empty array' in error for error in errors), errors
        )

    def test_schema3_repair_rejects_all_not_applicable_chain(self):
        def mutate(data):
            data['task_type'] = 'repair'
            for name in CHAIN_NAMES:
                data['chain'][name] = {'not_applicable': True, 'reason': 'x'}

        errors = self._errors(mutate)
        self.assertTrue(errors, errors)
        self.assertTrue(
            any('must be a non-empty array' in error for error in errors), errors
        )

    def test_schema3_prerequisite_accepts_structured_not_applicable_chain(self):
        def mutate(data):
            data['task_type'] = 'prerequisite'
            data['non_user_completion_reason'] = 'internal groundwork; no user-facing outcome'
            for name in CHAIN_NAMES:
                data['chain'][name] = {'not_applicable': True, 'reason': 'not part of this task'}

        self.assertEqual(self._errors(mutate), [])

    def test_schema3_vertical_feature_accepts_real_chain_references(self):
        def mutate(data):
            data['task_type'] = 'vertical-feature'
            for name in CHAIN_NAMES:
                data['chain'][name] = ['src/app.py']

        self.assertEqual(self._errors(mutate), [])

    def test_schema2_structured_not_applicable_behaviour_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'task.md'
            structured_chain = {
                name: {'not_applicable': True, 'reason': 'x'} for name in CHAIN_NAMES
            }
            data = json.loads(SCHEMA2_VALID.split('```pipeline-contract\n')[1].split('\n```')[0])
            data['chain'] = structured_chain
            sheet = (
                '# Task\n<!-- Task ID: demo -->\n```pipeline-contract\n'
                + json.dumps(data)
                + '\n```\n'
            )
            path.write_text(sheet, encoding='utf-8')
            errors = validate_task(path)
            self.assertTrue(
                any('must be a non-empty array' in error for error in errors), errors
            )
            path.write_text(SCHEMA2_VALID, encoding='utf-8')
            self.assertEqual(validate_task(path), [])

    def test_schema3_enforces_operation_resource_mode_match(self):
        errors = self._errors(
            lambda data: data['operations'][0].update({'resources': ['a.py', 'b.py']})
        )
        self.assertTrue(any('resource_mode' in error for error in errors), errors)

        def batch(data):
            data['operations'][0]['resources'] = ['a.py', 'b.py']
            data['operations'][0]['resource_mode'] = 'batch'

        self.assertEqual(self._errors(batch), [])

    def test_schema3_rejects_non_array_assumptions(self):
        errors = self._errors(lambda data: data.__setitem__('assumptions', 'not an array'))
        self.assertTrue(
            any('assumptions must be an array' in error for error in errors), errors
        )

    def test_schema3_rejects_non_object_assumption_records(self):
        errors = self._errors(lambda data: data.__setitem__('assumptions', [['nested']]))
        self.assertTrue(
            any('assumptions[1] must be an object' in error for error in errors), errors
        )

    def test_schema3_rejects_unsafe_unknown_ids(self):
        errors = self._errors(
            lambda data: data.__setitem__('unknowns', [{'id': 'bad id!'}])
        )
        self.assertTrue(
            any(
                'unknowns[1] id must be a safe identifier' in error for error in errors
            ),
            errors,
        )

    def test_schema3_accepts_empty_assumptions_and_unknowns(self):
        def mutate(data):
            data['assumptions'] = []
            data['unknowns'] = []

        self.assertEqual(self._errors(mutate), [])

    def test_schema3_accepts_contract_without_assumptions_or_unknowns(self):
        def mutate(data):
            data.pop('assumptions', None)
            data.pop('unknowns', None)

        self.assertEqual(self._errors(mutate), [])

    def test_schema3_accepts_well_formed_assumptions_and_unknowns(self):
        def mutate(data):
            data['assumptions'] = [{'id': 'assumption-1', 'text': 'the API stays stable'}]
            data['unknowns'] = [{'id': 'unknown-1', 'text': 'exact latency budget'}]

        self.assertEqual(self._errors(mutate), [])

    def test_schema3_requires_prerequisite_non_user_completion_reason(self):
        errors = self._errors(lambda data: data.__setitem__('task_type', 'prerequisite'))
        self.assertTrue(any('non_user_completion_reason' in error for error in errors), errors)

        def complete(data):
            data['task_type'] = 'prerequisite'
            data['non_user_completion_reason'] = 'internal groundwork; no user-facing outcome'

        self.assertEqual(self._errors(complete), [])

    def _derived_errors(self, mutate=None, parent_task_type='repair'):
        def base(data):
            data['task_type'] = 'derived'
            data['derived_from'] = {
                'task_id': 'parent-task',
                'commit': '0' * 40,
                'branch': 'parent-branch',
                'parent_task_type': parent_task_type,
            }
            if mutate is not None:
                mutate(data)

        return self._errors(base)

    def test_schema3_derived_task_requires_derived_from(self):
        errors = self._errors(
            lambda data: data.__setitem__(
                'task_type', 'derived'
            )
        )
        self.assertTrue(any('derived_from' in error for error in errors), errors)

    def test_schema3_derived_task_accepts_complete_derived_from(self):
        self.assertEqual(self._derived_errors(), [])

    def test_schema3_derived_task_rejects_tampered_parent_identity(self):
        for field in ('task_id', 'commit', 'branch'):
            with self.subTest(field=field):
                errors = self._derived_errors(
                    lambda data, field=field: data['derived_from'].__setitem__(field, '')
                )
                self.assertTrue(
                    any(f'derived_from.{field}' in error for error in errors), errors
                )

        errors = self._derived_errors(lambda data: data.__setitem__('derived_from', []))
        self.assertTrue(any('derived_from' in error for error in errors), errors)

    def test_schema3_derived_task_requires_valid_parent_task_type(self):
        errors = self._derived_errors(
            lambda data: data['derived_from'].pop('parent_task_type')
        )
        self.assertTrue(
            any('derived_from.parent_task_type' in error for error in errors), errors
        )

        errors = self._derived_errors(
            lambda data: data['derived_from'].__setitem__('parent_task_type', 'bogus')
        )
        self.assertTrue(
            any('derived_from.parent_task_type' in error for error in errors), errors
        )

        errors = self._derived_errors(
            lambda data: data['derived_from'].__setitem__('parent_task_type', '')
        )
        self.assertTrue(
            any('derived_from.parent_task_type' in error for error in errors), errors
        )

    def test_schema3_derived_from_vertical_feature_rejects_all_not_applicable_chain(self):
        def mutate(data):
            for name in CHAIN_NAMES:
                data['chain'][name] = {'not_applicable': True, 'reason': 'x'}

        errors = self._derived_errors(mutate, parent_task_type='vertical-feature')
        self.assertTrue(errors, errors)
        self.assertTrue(
            any('must be a non-empty array' in error for error in errors), errors
        )

    def test_schema3_derived_from_repair_rejects_all_not_applicable_chain(self):
        def mutate(data):
            for name in CHAIN_NAMES:
                data['chain'][name] = {'not_applicable': True, 'reason': 'x'}

        errors = self._derived_errors(mutate, parent_task_type='repair')
        self.assertTrue(errors, errors)
        self.assertTrue(
            any('must be a non-empty array' in error for error in errors), errors
        )

    def test_schema3_derived_from_vertical_feature_enforces_evidence_floor(self):
        def mutate(data):
            data['risk'] = 'low'
            data['acceptance_tests'][0]['evidence_level'] = 1
            data['required_evidence_levels'] = [1]

        errors = self._derived_errors(mutate, parent_task_type='vertical-feature')
        self.assertTrue(any('floor 2' in error for error in errors), errors)

    def test_schema3_derived_from_prerequisite_allows_not_applicable_and_low_evidence(self):
        def mutate(data):
            data['risk'] = 'low'
            data['acceptance_tests'][0]['evidence_level'] = 1
            data['required_evidence_levels'] = [1]
            for name in CHAIN_NAMES:
                data['chain'][name] = {'not_applicable': True, 'reason': 'not part of this task'}

        self.assertEqual(self._derived_errors(mutate, parent_task_type='prerequisite'), [])

    def test_schema1_and_schema2_derived_tasks_are_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'task.md'
            data = json.loads(SCHEMA2_VALID.split('```pipeline-contract\n')[1].split('\n```')[0])
            data['task_type'] = 'derived'
            sheet = (
                '# Task\n<!-- Task ID: demo -->\n```pipeline-contract\n'
                + json.dumps(data)
                + '\n```\n'
            )
            path.write_text(sheet, encoding='utf-8')
            self.assertEqual(validate_task(path), [])
            path.write_text(VALID, encoding='utf-8')
            self.assertEqual(validate_task(path), [])

    def test_schema3_rejects_abbreviated_acceptance_id(self):
        errors = self._errors(lambda data: data['acceptance_tests'][0].__setitem__('id', 'AT1'))
        self.assertTrue(any('id' in error for error in errors), errors)

    def test_schema3_enforces_evidence_floor(self):
        errors = self._errors(lambda data: data['acceptance_tests'][0].__setitem__('evidence_level', 1))
        self.assertTrue(any('floor' in error for error in errors), errors)

        def high_risk_web(data):
            data['risk'] = 'high'
            data['project_type'] = 'web'
            data['acceptance_tests'][0]['evidence_level'] = 4

        self.assertEqual(self._errors(high_risk_web), [])

        def web_below_floor(data):
            data['risk'] = 'medium'
            data['project_type'] = 'web'
            data['acceptance_tests'][0]['evidence_level'] = 2

        errors = self._errors(web_below_floor)
        self.assertTrue(any('floor 3' in error for error in errors), errors)

    def test_schema1_and_schema2_outcomes_unchanged_by_schema3_rules(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'task.md'
            path.write_text(VALID, encoding='utf-8')
            self.assertEqual(validate_task(path), [])
            path.write_text(SCHEMA2_VALID, encoding='utf-8')
            self.assertEqual(validate_task(path), [])
            legacy_chain = SCHEMA2_VALID.replace(
                '"entry":["cli.py"]', '"entry":["not-applicable"]'
            )
            path.write_text(legacy_chain, encoding='utf-8')
            self.assertEqual(validate_task(path), [])


if __name__ == '__main__':
    unittest.main()
