# Executor report

- task-id: `acceptance-id-and-template-compliance`
- worktree: `D:/Projects/Skills/pipeline/.worktrees/acceptance-id-and-template-compliance`
- branch: `acceptance-id-and-template-compliance`
- round: 2
- role: executor
- product commit: `96af91f`
- product_head: `96af91f8a11f005b3e45f06119442ba9f9cb8f64`
- evidence head: `5af1ae0999a143fdb4ce38df7cd5c57e6b580534`
- contract: `3714e50e17ea9e49a5fc9675e20052f25bee90b7`

## Commands

| Command | Exit code | Assertion |
|---|---:|---|
| `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance -v` | 0 | 7 frozen compliance tests passed |
| `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_contract tests.test_planning_dispatch_integration tests.test_derived_task_dispatch_recovery -v` | 0 | 15 focused contract/dispatch/recovery tests passed |
| `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v` | 0 | 142 tests passed |
| `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/acceptance-id-and-template-compliance.md` | 0 | current schema 2 task validates |
| `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight . --contract 3714e50 --task-sheet docs/tasks/acceptance-id-and-template-compliance.md --expected-head 5af1ae0999a143fdb4ce38df7cd5c57e6b580534 --expected-branch acceptance-id-and-template-compliance --expected-worktree D:/Projects/Skills/pipeline/.worktrees/acceptance-id-and-template-compliance --run-id acceptance-final` | 0 | identity and frozen contract preflight passed |
| `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task freeze-check . --contract 3714e50 --task-sheet docs/tasks/acceptance-id-and-template-compliance.md --expected-head 5af1ae0999a143fdb4ce38df7cd5c57e6b580534 --expected-branch acceptance-id-and-template-compliance --expected-worktree D:/Projects/Skills/pipeline/.worktrees/acceptance-id-and-template-compliance --run-id acceptance-final` | 0 | freeze check passed |
| `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --task-id acceptance-id-and-template-compliance --allowed 'docs/tasks/pipeline-tools-v1.md' 'docs/tasks/pipeline-evidence-lifecycle-migration.md' 'docs/tasks/pipeline-tools-v1-continuation-1.md' 'references/acceptance-evidence.md' 'tests/test_acceptance_id_and_template_compliance.py' '.pipeline/acceptance-id-and-template-compliance/**' --forbidden implement-plan.md IDEA.md '.pipeline/metrics/**' 'docs/tasks/** other new task sheets' '.worktrees/**' 'metrics/**'` | 0 | changed paths stayed in frozen scope |
| `git diff --check` | 0 | no whitespace errors |

## Observed changes

- Migrated all explicit acceptance IDs in the three frozen `docs/tasks/pipeline*.md` sheets from `AT*` to `acceptance-test-*`, including ledger references.
- Added exact compliance tests covering schema 2 rejection, schema 1 read-only compatibility, frozen references, template format, and forbidden scope.
- Added the acceptance-ID policy to `references/acceptance-evidence.md`.
- No metrics command was run; `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` was used for all pipeline/test commands.

## Unverified

- Independent reviewer re-run and final merge gate are not performed in this executor report.

```pipeline-evidence
{"schema":1,"task_id":"acceptance-id-and-template-compliance","worktree":"D:/Projects/Skills/pipeline/.worktrees/acceptance-id-and-template-compliance","branch":"acceptance-id-and-template-compliance","role":"executor","round":2,"status":"PASS","commands":[{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance -v","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/acceptance-id-and-template-compliance.md","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --task-id acceptance-id-and-template-compliance --allowed docs/tasks/pipeline-tools-v1.md docs/tasks/pipeline-evidence-lifecycle-migration.md docs/tasks/pipeline-tools-v1-continuation-1.md references/acceptance-evidence.md tests/test_acceptance_id_and_template_compliance.py .pipeline/acceptance-id-and-template-compliance/** --forbidden implement-plan.md IDEA.md .pipeline/metrics/** docs/tasks/** other new task sheets .worktrees/** metrics/**","exit_code":0,"evidence_ref":"executor-report.md"}],"assertions":["7 compliance tests passed","142 full-suite tests passed","three migrated task sheets validate","scope and diff checks passed"],"evidence_refs":["executor-report.md"],"unverified":["independent reviewer re-run","final merge gate"],"identity":{"head":"5af1ae0999a143fdb4ce38df7cd5c57e6b580534","product_head":"96af91f8a11f005b3e45f06119442ba9f9cb8f64","contract":"3714e50e17ea9e49a5fc9675e20052f25bee90b7"},"recommendation":"ready_for_review"}
```
