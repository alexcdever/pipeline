# Main-agent final check

- Task: `planning-facts-conflict-model`
- Worktree: `D:/Projects/Skills/pipeline/.worktrees/planning-facts-conflict-model`
- Branch: `planning-facts-conflict-model`
- HEAD: `9e9fcc9727b4a2ea2d9726fe6e9d227de5a7a0f7`
- Product/test head: `17f26fe6c58aa5f73c3012e03b51a49a70815d09`
- Contract: `a818e08`
- Role: `main-final`
- Round: 2

## Final verification

The prior placeholder was discarded and this report was generated from the commands listed below. All commands were run from the reviewed worktree with `DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` where applicable.

- Frozen acceptance tests 1–3: PASS, each exit code 0.
- Full regression: PASS, `Ran 123 tests`, `OK`.
- Task contract validation: PASS.
- Task preflight and freeze-check at the exact reviewed HEAD: PASS.
- Scope check: PASS; only permitted product/test/evidence paths are present relative to product head.
- `git diff --check 17f26fe..HEAD`: PASS.
- Executor result verification: PASS.
- Evidence freshness: PASS; post-product-head changes are evidence-only executor artifacts.
- Evidence readiness and evidence verification: PASS.
- Reviewer result verification: PASS after reviewer status was updated to PASS.
- Pre-merge gate: PASS after all evidence was regenerated.
- Unauthorized resolution and conflict gate were independently verified by reviewer: fail-closed and blocking respectively.

## Decision

All required product and evidence checks pass. This final check is trusted and authorizes evidence finalization.

```pipeline-evidence
{"schema":1,"task_id":"planning-facts-conflict-model","worktree":"D:/Projects/Skills/pipeline/.worktrees/planning-facts-conflict-model","branch":"planning-facts-conflict-model","role":"main-final","round":2,"status":"PASS","identity":{"product_head":"17f26fe6c58aa5f73c3012e03b51a49a70815d09","review_head":"9e9fcc9727b4a2ea2d9726fe6e9d227de5a7a0f7","contract":"a818e08"},"commands":[{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_facts_are_classified_with_sources_and_safe_identity -v","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_conflicts_block_planning_and_preserve_decision_records -v","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_invalid_facts_and_unauthorized_resolution_are_rejected -v","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json task validate docs/tasks/planning-facts-conflict-model.md","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json task preflight . --contract a818e08 --task-sheet docs/tasks/planning-facts-conflict-model.md --expected-head 9e9fcc9727b4a2ea2d9726fe6e9d227de5a7a0f7 --expected-branch planning-facts-conflict-model --expected-worktree .","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freeze-check . --contract a818e08 --task-sheet docs/tasks/planning-facts-conflict-model.md --expected-head 9e9fcc9727b4a2ea2d9726fe6e9d227de5a7a0f7 --expected-branch planning-facts-conflict-model --expected-worktree .","exit_code":0,"evidence_ref":"final-check.md"},{"command":"git diff --check 17f26fe..HEAD","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json scope check . --task-id planning-facts-conflict-model --allowed pipeline_tools/planning.py tests/test_planning_facts_conflicts.py .pipeline/planning-facts-conflict-model/** --forbidden implement-plan.md IDEA.md docs/tasks/** .pipeline/metrics/**","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/planning-facts-conflict-model/executor-result.json --task-id planning-facts-conflict-model --role executor","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/planning-facts-conflict-model --result .pipeline/planning-facts-conflict-model/executor-result.json","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json evidence readiness .pipeline/planning-facts-conflict-model --task-id planning-facts-conflict-model","exit_code":0,"evidence_ref":"final-check.md"},{"command":"DISABLE_AUTO_METRICS=1 PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json evidence verify .pipeline/planning-facts-conflict-model --task-id planning-facts-conflict-model --branch planning-facts-conflict-model","exit_code":0,"evidence_ref":"final-check.md"}],"assertions":["three frozen acceptance tests pass","full regression has 123 passing tests","contract, identity, scope, whitespace, result, freshness and evidence checks pass","reviewer independently confirmed fail-closed unauthorized resolution and conflict gate","no product, test, task-sheet, implement-plan or IDEA files were changed by final evidence work"],"evidence_refs":["final-check.md","final-result.json","reviewer-result.json"],"unverified":[]}
```
