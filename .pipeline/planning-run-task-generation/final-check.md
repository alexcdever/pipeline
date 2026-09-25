# Final check

- task-id: `planning-run-task-generation`
- role: `main-final`
- round: `1`
- worktree: `D:/Projects/Skills/pipeline/.worktrees/planning-run-task-generation`
- branch: `planning-run-task-generation`
- current HEAD: `5696f7a27ba38fb7379b4d14591b4f4c9d5ed230`
- product/test baseline: `d7c83ef3ff585c876ffde381001cf94ae4792201`
- status: **READY-TO-MERGE**

## Final verification

- `pipeline-tools task validate docs/tasks/planning-run-task-generation.md`: exit 0.
- 验收测试1–5：exit 0。
- 验收测试6 / 全量回归：101 tests passed，exit 0。
- `pipeline-tools scope check`: exit 0。
- `git diff --check`: exit 0。
- executor `result verify`: exit 0。
- executor `freshness`: exit 0；product/test baseline 与当前 HEAD 之间仅有 evidence-only 提交。
- reviewer `result verify`: exit 0。
- reviewer `freshness`: exit 0；product/test baseline 与当前 HEAD 之间仅有 evidence-only 提交。
- 未修改产品代码、测试、冻结任务单、`implement-plan.md`、`IDEA.md`。
- 未提交 metrics。

```pipeline-evidence
{"schema":1,"task_id":"planning-run-task-generation","worktree":"D:/Projects/Skills/pipeline/.worktrees/planning-run-task-generation","branch":"planning-run-task-generation","role":"main-final","round":1,"status":"READY-TO-MERGE","commands":[{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/planning-run-task-generation.md","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_valid_plan_creates_schema2_task_sheets tests.test_task_generation.TaskGenerationTests.test_generation_rejects_invalid_inputs_and_preserves_failure_artifacts tests.test_task_generation.TaskGenerationTests.test_generation_is_fail_closed_for_existing_tasks_duplicate_ids_and_unsafe_output tests.test_task_generation.TaskGenerationTests.test_generation_rejects_implement_plan_hash_drift_and_checks_plan_sheet_consistency tests.test_cli.CLITests.test_planning_generate_task_sheets_cli_lifecycle -v","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --allowed pipeline_tools/** tests/** .pipeline/planning-run-task-generation/** --forbidden implement-plan.md IDEA.md .pipeline/metrics/**","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 git diff --check","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/planning-run-task-generation/executor-result.json --task-id planning-run-task-generation --role executor --run-id planning-run-task-generation","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/executor-result.json"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools freshness . .pipeline/planning-run-task-generation --result .pipeline/planning-run-task-generation/executor-result.json --run-id planning-run-task-generation","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/executor-result.json"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/planning-run-task-generation/reviewer-result.json --task-id planning-run-task-generation --role reviewer --run-id review-20260925-r3","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/reviewer-result.json"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools freshness . .pipeline/planning-run-task-generation --result .pipeline/planning-run-task-generation/reviewer-result.json --run-id review-20260925-r3","exit_code":0,"evidence_ref":".pipeline/planning-run-task-generation/reviewer-result.json"}],"assertions":["acceptance-test-1 through acceptance-test-6 pass","101 regression tests pass","task contract, scope, and whitespace checks pass","executor and reviewer result verification and freshness pass","product/test baseline is d7c83ef and current HEAD is f5f7319","decision is ready for evidence finalization"],"evidence_refs":[".pipeline/planning-run-task-generation/final-check.md",".pipeline/planning-run-task-generation/executor-result.json",".pipeline/planning-run-task-generation/reviewer-result.json"],"unverified":[]}
```
