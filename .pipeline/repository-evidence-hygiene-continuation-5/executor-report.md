# Executor report

```pipeline-evidence
{
  "schema":1,
  "task_id":"repository-evidence-hygiene-continuation-5",
  "worktree":"D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene",
  "branch":"repository-evidence-hygiene",
  "role":"executor",
  "round":5,
  "status":"PASS",
  "identity":{"product_head":"ba1ac15","contract":"cd79ce7","head":"644291ac032b98f5cbd611ef5df9b0bb52866892","evidence_only":true},
  "commands":[
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head $(git rev-parse HEAD) --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task freeze-check . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head $(git rev-parse HEAD) --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/repository-evidence-hygiene-continuation-5/executor-result.json --task-id repository-evidence-hygiene-continuation-5 --role executor","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools freshness . .pipeline/repository-evidence-hygiene-continuation-5 --result .pipeline/repository-evidence-hygiene-continuation-5/executor-result.json","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --task-id repository-evidence-hygiene-continuation-5 --allowed pipeline_tools/** tests/** docs/tasks/** references/** .pipeline/repository-evidence-hygiene-continuation-5/** .pipeline/metrics/** --forbidden implement-plan.md IDEA.md .pipeline/*/product/** .pipeline/*/historical/**","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"for task in docs/tasks/*.md; do python scripts/validate_task_sheet.py \"$task\" || exit $?; done","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"git diff --check ba1ac15..HEAD","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"}
  ],
  "assertions":["all prerequisites pass","all 16 task sheets validate","149 tests pass","evidence is only changed scope","metrics were not cleaned"],
  "evidence_refs":[".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"],
  "unverified":[]
}
```

The earlier stale-head and wrong-argument attempts were diagnosis-only and are omitted from the mergeable command set. This report records only the final successful evidence run.
