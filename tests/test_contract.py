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


if __name__ == '__main__':
    unittest.main()
