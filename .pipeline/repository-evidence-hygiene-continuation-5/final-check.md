# Main final check

Final check completed against product/test HEAD `ba1ac15`, frozen contract `cd79ce7`, and evidence HEAD `644291ac032b98f5cbd611ef5df9b0bb52866892`. This phase changes evidence only. No product, test, task sheet, `implement-plan.md`, `IDEA.md`, or metrics files were modified.

```pipeline-evidence
{
  "schema":1,
  "task_id":"repository-evidence-hygiene-continuation-5",
  "worktree":"D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene",
  "branch":"repository-evidence-hygiene",
  "role":"main-final",
  "round":1,
  "status":"PASS",
  "identity":{"product_head":"ba1ac15","contract":"cd79ce7","head":"644291ac032b98f5cbd611ef5df9b0bb52866892","evidence_only":true},
  "commands":[
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head $(git rev-parse HEAD) --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task freeze-check . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head $(git rev-parse HEAD) --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/repository-evidence-hygiene-continuation-5/executor-result.json --task-id repository-evidence-hygiene-continuation-5 --role executor","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/repository-evidence-hygiene-continuation-5/reviewer-result.json --task-id repository-evidence-hygiene-continuation-5 --role reviewer","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools freshness . .pipeline/repository-evidence-hygiene-continuation-5 --result .pipeline/repository-evidence-hygiene-continuation-5/executor-result.json","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --task-id repository-evidence-hygiene-continuation-5 --allowed pipeline_tools/** tests/** docs/tasks/** references/** .pipeline/repository-evidence-hygiene-continuation-5/** .pipeline/metrics/** --forbidden implement-plan.md IDEA.md .pipeline/*/product/** .pipeline/*/historical/**","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"},
    {"command":"for task in docs/tasks/*.md; do python scripts/validate_task_sheet.py \"$task\" || exit $?; done","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"},
    {"command":"git diff --check ba1ac15..HEAD","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"}
  ],
  "assertions":["all real prerequisites passed","all 16 task sheets validate","full regression passed: 149 tests","only evidence files are changed after product/test HEAD","metrics were not cleaned","finalization is authorized"],
  "evidence_refs":[".pipeline/repository-evidence-hygiene-continuation-5/final-check.md"],
  "unverified":[]
}
```
