# Executor report

```pipeline-evidence
{
  "schema": 1,
  "task_id": "task-evidence-reconcile",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/task-evidence-reconcile",
  "branch": "task-evidence-reconcile",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "commands": [
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest -v tests.test_task_evidence_reconcile", "exit_code": 0, "evidence_ref": "reconcile-focused.log"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -p 'test_*.py'", "exit_code": 0, "evidence_ref": "reconcile-full.log"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools runtime preflight .", "exit_code": 0, "evidence_ref": "reconcile-gates.log"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/task-evidence-reconcile.md", "exit_code": 0, "evidence_ref": "reconcile-gates.log"}
  ],
  "assertions": [
    "default reconcile is read-only",
    "update changes only the task status section",
    "identity conflict and missing evidence never claim PASS",
    "focused and full unittest suites pass",
    "runtime and task validation pass"
  ],
  "evidence_refs": ["reconcile-focused.log", "reconcile-full.log", "reconcile-gates.log"],
  "unverified": ["independent review", "final-check", "scope check while pre-existing untracked metrics exists"]
}
```

Executor evidence records only directly run commands and leaves review/finalization unverified.
