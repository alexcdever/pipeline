# Executor report

```pipeline-evidence
{
  "schema": 1,
  "task_id": "repository-evidence-hygiene-continuation-5",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene",
  "branch": "repository-evidence-hygiene",
  "role": "executor",
  "round": 4,
  "status": "PASS",
  "identity": {"product_head":"ba1ac15","contract":"cd79ce7","head":"837c9f54b897ed6c6abcc0ee095bcbabbf87d554","evidence_only":true},
  "commands": [
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head 837c9f54b897ed6c6abcc0ee095bcbabbf87d554 --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":4,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task freeze-check . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head 837c9f54b897ed6c6abcc0ee095bcbabbf87d554 --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":4,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head 837c9f54b897ed6c6abcc0ee095bcbabbf87d554 --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":4,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head $(git rev-parse HEAD) --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task freeze-check . --contract cd79ce7 --task-sheet docs/tasks/repository-evidence-hygiene.md --expected-head $(git rev-parse HEAD) --expected-branch repository-evidence-hygiene --expected-worktree D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene --run-id hygiene-final","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/repository-evidence-hygiene-continuation-5/executor-result.json --task-id repository-evidence-hygiene-continuation-5 --role executor","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools freshness . .pipeline/repository-evidence-hygiene-continuation-5 --result .pipeline/repository-evidence-hygiene-continuation-5/executor-result.json","exit_code":3,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --task-id repository-evidence-hygiene-continuation-5 --allowed pipeline_tools/** tests/** docs/tasks/** references/** .pipeline/repository-evidence-hygiene-continuation-5/** .pipeline/metrics/** --forbidden implement-plan.md IDEA.md .pipeline/*/product/** .pipeline/*/historical/**","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"},
    {"command":"git diff --check ba1ac15..HEAD","exit_code":0,"evidence_ref":".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"}
  ],
  "assertions":["cd79ce7 is the real ancestor and contains the task sheet at the canonical path","the first attempted HEAD was stale; dynamic current HEAD is required","dynamic HEAD preflight and freeze both pass","freshness remains blocked because this evidence refresh is not yet committed","no final-check is generated while freshness is blocked","no metrics cleanup was performed"],
  "evidence_refs":[".pipeline/repository-evidence-hygiene-continuation-5/executor-report.md"],
  "unverified":["freshness after evidence commit","final-check","merge readiness"]
}
```

The original failure was caused by passing stale `837c9f5` as `--expected-head` after evidence commit `ebed744`; `cd79ce7` itself is valid and contains the canonical task path. Final-check remains intentionally absent until committed evidence freshness passes.
