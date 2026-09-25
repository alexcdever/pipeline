# Final Check — dispatch-fail-closed-and-approval-semantics

- task-id: `dispatch-fail-closed-and-approval-semantics`
- worktree: `D:/Projects/Skills/pipeline/.worktrees/dispatch-fail-closed-and-approval-semantics`
- branch: `dispatch-fail-closed-and-approval-semantics`
- HEAD: `fe70cbe5be815f052d7aeeca90508cc5995dad3`
- role: `main-final`
- round: `1`
- metrics: disabled with `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1`

## Final decision

产品与证据闭环 PASS。没有修改产品代码、测试、任务单、`implement-plan.md` 或 `IDEA.md`。审查结论从 BLOCKED 更新为 PASS 的唯一阻塞项是 final-check 缺失；该文件及对应机器结果现已在同一 worktree 生成。

## Verification

- 冻结验收 1–6：全部退出码 0。
- 冻结验收 7：全量 `unittest discover`，`Ran 131 tests`，`OK`，退出码 0。
- 冻结验收 8：任务单校验退出码 0。
- `task preflight`、`task freeze-check`：使用当前 HEAD、分支和绝对 worktree 的命令通过；旧 executor 报告中绑定旧 HEAD 的命令不作为当前证据。
- `scope check`、`git diff --check`：通过；产品范围仅包含冻结允许的三个产品/测试文件。
- executor `result verify` 和 `freshness`：通过。
- final evidence `readiness`、`evidence verify`、`gate pre-merge`、`gate post-merge`：生成 final evidence 后通过。
- `evidence-finalize --success`：通过，生成 `finalization.json`，仅保留契约要求的 evidence 文件及被引用文件。

## Acceptance semantics confirmed

- same/different/hash-drift 三类已有任务单冲突均 fail-closed，保留冲突 artifact，不覆盖任务单或已有 worktree。
- automatic 不要求显式 approve；manual 在 approval 前 blocked 且不创建 worktree，显式 approve 后才 dispatch。
- 阶段失败停止下游并保留审计 artifact、errors 和 next actions。
- `dispatch-ready` 不推断 executor/reviewer PASS。

```pipeline-evidence
{"schema":1,"task_id":"dispatch-fail-closed-and-approval-semantics","worktree":"D:/Projects/Skills/pipeline/.worktrees/dispatch-fail-closed-and-approval-semantics","branch":"dispatch-fail-closed-and-approval-semantics","round":1,"role":"main-final","status":"PASS","commands":[{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_failure_does_not_create_or_replace_worktree -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_automatic_approval_dispatches_without_explicit_approve -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_manual_approval_requires_explicit_approve_before_dispatch -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_lifecycle.PlanningLifecycleTests.test_manual_finalize_requires_approval_but_automatic_finalize_does_not -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/dispatch-fail-closed-and-approval-semantics.md","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools evidence readiness . --task-id dispatch-fail-closed-and-approval-semantics","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools evidence verify .pipeline/dispatch-fail-closed-and-approval-semantics --task-id dispatch-fail-closed-and-approval-semantics --branch dispatch-fail-closed-and-approval-semantics","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools gate pre-merge . --task-id dispatch-fail-closed-and-approval-semantics --branch dispatch-fail-closed-and-approval-semantics --result .pipeline/dispatch-fail-closed-and-approval-semantics/final-result.json --role main-final","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools gate post-merge . --task-id dispatch-fail-closed-and-approval-semantics --branch dispatch-fail-closed-and-approval-semantics --result .pipeline/dispatch-fail-closed-and-approval-semantics/final-result.json --role main-final","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md"}],"assertions":["all eight frozen acceptance tests pass","full regression passes with 131 tests","task validate, preflight, freeze-check, scope, diff, result verify, freshness pass","evidence readiness and evidence verify pass","pre-merge and post-merge gates pass","automatic/manual approval and fail-closed conflict semantics are confirmed","no forbidden product or task files changed"],"evidence_refs":[".pipeline/dispatch-fail-closed-and-approval-semantics/final-check.md",".pipeline/dispatch-fail-closed-and-approval-semantics/final-result.json"],"unverified":[],"recommendation":"READY_FOR_EVIDENCE_FINALIZATION"}
```
