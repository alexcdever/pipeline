# Final check

```pipeline-evidence
{
  "schema": 1,
  "task_id": "pipeline-evidence-lifecycle-migration-continuation-1",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/pipeline-evidence-lifecycle-migration-continuation-1",
  "branch": "pipeline-evidence-lifecycle-migration-continuation-1",
  "role": "main-final",
  "round": 2,
  "status": "PASS",
  "commands": [
    {"command": "python -m pipeline_tools task validate docs/tasks/pipeline-evidence-lifecycle-migration-continuation-1.md", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m pipeline_tools runtime preflight . --require python", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m pipeline_tools task freeze-check . --contract ddfa8aa880d422be8c8b9e4518a2281e07fca910 --task-sheet docs/tasks/pipeline-evidence-lifecycle-migration-continuation-1.md --expected-head a2eb267e34f49a845a39d9d17efe7dd6d02417cb --expected-branch pipeline-evidence-lifecycle-migration-continuation-1 --expected-worktree D:/Projects/Skills/pipeline/.worktrees/pipeline-evidence-lifecycle-migration-continuation-1", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m pipeline_tools scope history . --evidence-root .pipeline/pipeline-evidence-lifecycle-migration-continuation-1", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m unittest discover -s tests -v", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"}
  ],
  "assertions": ["All frozen acceptance tests and full regression passed.", "Task identity, scope history guard, finalization and finalized verification are mechanically checked.", "Parent task remains BLOCKED and prohibited files remain untouched."],
  "evidence_refs": [".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"],
  "unverified": []
}
```
