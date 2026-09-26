# Executor report

```pipeline-evidence
{
  "schema": 1,
  "task_id": "repository-evidence-hygiene-continuation-5",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene",
  "branch": "repository-evidence-hygiene",
  "role": "executor",
  "round": 3,
  "status": "PASS",
  "identity": {"product_head":"ba1ac15","contract":"cd79ce7","head":"837c9f54b897ed6c6abcc0ee095bcbabbf87d554","evidence_only":true},
  "commands": [
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools runtime preflight . --task-id repository-evidence-hygiene-continuation-5 --run-id hygiene-refresh","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/repository-evidence-hygiene.md","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight . --contract docs/tasks/repository-evidence-hygiene.md --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head 837c9f54b897ed6c6abcc0ee095bcbabbf87d554 --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-refresh","exit_code":4,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task freeze-check . --contract docs/tasks/repository-evidence-hygiene.md --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head 837c9f54b897ed6c6abcc0ee095bcbabbf87d554 --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-refresh","exit_code":4,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"for task in docs/tasks/*.md; do python scripts/validate_task_sheet.py \"$task\" || exit $?; done","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/repository-evidence-hygiene-continuation-5/executor-result.json --task-id repository-evidence-hygiene-continuation-5 --role executor","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools freshness . .pipeline/repository-evidence-hygiene-continuation-5 --result .pipeline/repository-evidence-hygiene-continuation-5/executor-result.json","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --task-id repository-evidence-hygiene-continuation-5 --allowed pipeline_tools/** tests/** docs/tasks/** references/** .pipeline/repository-evidence-hygiene-continuation-5/** .pipeline/metrics/** --forbidden implement-plan.md IDEA.md .pipeline/*/product/** .pipeline/*/historical/**","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"git diff --check ba1ac15..HEAD","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"}
  ],
  "assertions":["identity is bound to product_head ba1ac15, contract cd79ce7, and evidence head 837c9f54b897ed6c6abcc0ee095bcbabbf87d554","149 tests pass","all task sheets validate","result verify, freshness, scope, and diff pass","preflight/freeze report unavailable contract commit without changing contract","no metrics cleanup"],
  "evidence_refs":[".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"],
  "unverified":["independent review","final-check","merge readiness"]
}
```

Evidence-only refresh. Historical acceptance outcomes remain UNVERIFIED; no product, test, task-sheet, plan, IDEA, or metrics files were changed.
