# Final check

- task-id: `acceptance-id-and-template-compliance`
- role: `main-final`
- round: 1
- worktree: `D:/Projects/Skills/pipeline/.worktrees/acceptance-id-and-template-compliance`
- branch: `acceptance-id-and-template-compliance`
- reviewer evidence HEAD: `95c9411a42153a8d0aad2ee4ceac23f7680fd894`
- product/test HEAD: `ba7e80d8f02018226e4fe6cd6c7a42f408ceefd1`
- frozen contract: `3714e50e17ea9e49a5fc9675e20052f25bee90b7`

The final check confirms the frozen acceptance suite, related suite, full regression, task-sheet validation, result verification, freshness, scope, and diff checks. No product, task sheet, IDEA, implement-plan, or metrics file was changed by this final-check phase.

```pipeline-evidence
{"schema":1,"task_id":"acceptance-id-and-template-compliance","worktree":"D:/Projects/Skills/pipeline/.worktrees/acceptance-id-and-template-compliance","branch":"acceptance-id-and-template-compliance","role":"main-final","round":1,"status":"READY-TO-MERGE","commands":[{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance -v","exit_code":0,"evidence_ref":"final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_contract tests.test_planning_dispatch_integration tests.test_derived_task_dispatch_recovery -v","exit_code":0,"evidence_ref":"final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":"final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/acceptance-id-and-template-compliance.md","exit_code":0,"evidence_ref":"final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools freshness . .pipeline/acceptance-id-and-template-compliance --result .pipeline/acceptance-id-and-template-compliance/executor-result.json --run-id final-check","exit_code":0,"evidence_ref":"final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --task-id acceptance-id-and-template-compliance --allowed docs/tasks/pipeline-tools-v1.md docs/tasks/pipeline-evidence-lifecycle-migration.md docs/tasks/pipeline-tools-v1-continuation-1.md references/acceptance-evidence.md tests/test_acceptance_id_and_template_compliance.py .pipeline/acceptance-id-and-template-compliance/** --forbidden implement-plan.md IDEA.md .pipeline/metrics/** docs/tasks/** other new task sheets .worktrees/** metrics/**","exit_code":0,"evidence_ref":"final-check.md"},{"command":"git diff --check 3714e50...HEAD","exit_code":0,"evidence_ref":"final-check.md"}],"assertions":["acceptance-test-1 through acceptance-test-7 pass","7 focused tests, 15 related tests, and 142 full tests pass","task validation, freshness, scope, and diff checks pass","product/test head is ba7e80d and contract is 3714e50"],"evidence_refs":["final-check.md","final-result.json"],"unverified":[]}
```

Decision: `READY_FOR_EVIDENCE_FINALIZATION`
