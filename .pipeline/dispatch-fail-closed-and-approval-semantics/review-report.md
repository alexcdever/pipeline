# Reviewer Report — dispatch-fail-closed-and-approval-semantics

- task-id: `dispatch-fail-closed-and-approval-semantics`
- worktree: `D:/Projects/Skills/pipeline/.worktrees/dispatch-fail-closed-and-approval-semantics`
- branch: `dispatch-fail-closed-and-approval-semantics`
- HEAD: `fe70cbe5be815f052d7aeeca90508cc5995dad3`
- role: `reviewer`
- round: `1`
- metrics: disabled with `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1`

## 结论

**PASS：产品聚焦验收、全量回归和最终检查均通过。** final-check 已由 main final-check 在同一 worktree 生成并通过全部证据闸门；未发现产品或范围问题。

## 独立复验

冻结八项中的六项聚焦测试全部通过，逐项退出码 0：

- `test_stage_failures_stop_downstream_and_preserve_artifacts`
- `test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts`
- `test_dispatch_failure_does_not_create_or_replace_worktree`
- `test_automatic_approval_dispatches_without_explicit_approve`
- `test_manual_approval_requires_explicit_approve_before_dispatch`
- `test_manual_finalize_requires_approval_but_automatic_finalize_does_not`

全量命令 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`：退出码 0，`Ran 131 tests`，`OK`。

流程复验：

- `task validate docs/tasks/dispatch-fail-closed-and-approval-semantics.md`：退出码 0。
- `task preflight` / `task freeze-check` 使用当前 HEAD `fe70cbe5be815f052d7aeeca90508cc5995dad3`、当前分支和绝对 worktree：均退出码 0。
- executor 报告中以旧产品 HEAD `846aa69...` 重跑的 preflight/freeze 命令在当前 HEAD 上真实失败（`HEAD does not match expected head`）；这属于报告新鲜度/身份陈旧，不被当作当前产品失败。改用审查时直接读取的当前 HEAD 后两项通过。
- `scope check`：退出码 0；产品/测试变更仅为 `pipeline_tools/planning.py`、`tests/test_planning_dispatch_integration.py`、`tests/test_planning_lifecycle.py`，未发现任务单、`implement-plan.md`、`IDEA.md` 或父任务变更。
- `git diff --check eb52c41..HEAD`（允许产品/测试范围）：退出码 0。
- `result verify`：退出码 0。
- `freshness`：退出码 0，接受任务证据提交后的证据变更。
- `evidence readiness`：final-check 生成后通过，退出码 0。
- `evidence verify`、`gate pre-merge` 和 `gate post-merge`：final evidence 生成后按真实结果复验通过。
- `evidence-finalize --success`：通过，生成 `finalization.json` 并按保留引用规则完成成功清理。

## 语义审查

### 三类已有任务单冲突

集成测试明确覆盖并通过三类冲突：

1. **same**：同一 task、同一输入的重复生成/派发被 task-generation 阶段阻断；原任务单字节内容保持不变，已有 worktree 数量不增加。
2. **different**：同一 task 但输入计划发生变化被阻断；未进入 contract/freeze/identity/dispatch，不借用另一 run 的身份。
3. **hash-drift**：已有任务单被修改后被阻断；修改内容保留，不能通过覆盖任务单消除冲突。

代码路径 `planning_to_dispatch` 在 `generate_task_sheets` 非 pass 时立即返回，未执行下游阶段；`create_worktree_dispatch` 也在 task sheet、baseline、注册 worktree、branch 和目标占用检查失败时 fail-closed。该行为与冻结契约一致。

### automatic/manual approval

- `approval_mode=automatic` 不插入 approval stage，完整有效链路可在无 `approved=True` 时到达 `dispatch-ready`；其他 preflight/facts/contract/freeze/identity gate 仍执行。
- `approval_mode=manual` 在 freeze 后、dispatch-identity 前检查显式 approval；缺失时返回 `blocked`，不创建 worktree；显式 approval 后才创建唯一 worktree。
- lifecycle finalize 同样保持 automatic 无需 approval、manual 必须 approval，identity drift 优先阻断。
- `dispatch-ready` 的 next action 明确要求单独启动 executor，不推断 executor/reviewer PASS。

### 审计与无 worktree

每个阶段通过 `stage()` 写入带 run/task identity 的 JSON artifact；失败阶段立即停止并把 errors/blockers/next_actions 放入聚合结果。manual approval 阻塞发生在 worktree 创建之前。冲突和重复派发测试证明已有任务单、既有 worktree 内容及数量不被覆盖或替换。`write_dispatch` 使用临时文件后原子替换，但仅在 worktree identity 验证成功后调用。

## 范围与待办

本轮只更新 reviewer evidence，并新增 main final-check evidence；未修改产品代码、测试、任务单、`implement-plan.md` 或 `IDEA.md`。metrics 始终禁用，既有及本轮新增 metrics 均未清理。最终 evidence 仅保留契约要求的报告与机器结果。

```pipeline-evidence
{"schema":1,"task_id":"dispatch-fail-closed-and-approval-semantics","worktree":"D:/Projects/Skills/pipeline/.worktrees/dispatch-fail-closed-and-approval-semantics","branch":"dispatch-fail-closed-and-approval-semantics","role":"reviewer","round":1,"status":"PASS","commands":[{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_failure_does_not_create_or_replace_worktree -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_automatic_approval_dispatches_without_explicit_approve -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_manual_approval_requires_explicit_approve_before_dispatch -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_lifecycle.PlanningLifecycleTests.test_manual_finalize_requires_approval_but_automatic_finalize_does_not -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/dispatch-fail-closed-and-approval-semantics.md","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight . --contract eb52c41957e0fb81b9f95a60dfc30fb94fab53c9 --task-sheet docs/tasks/dispatch-fail-closed-and-approval-semantics.md --expected-branch dispatch-fail-closed-and-approval-semantics --expected-worktree D:/Projects/Skills/pipeline/.worktrees/dispatch-fail-closed-and-approval-semantics","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools task freeze-check . --contract eb52c41957e0fb81b9f95a60dfc30fb94fab53c9 --task-sheet docs/tasks/dispatch-fail-closed-and-approval-semantics.md --expected-branch dispatch-fail-closed-and-approval-semantics --expected-worktree D:/Projects/Skills/pipeline/.worktrees/dispatch-fail-closed-and-approval-semantics","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --allowed pipeline_tools/planning.py tests/test_planning_dispatch_integration.py tests/test_planning_lifecycle.py .pipeline/dispatch-fail-closed-and-approval-semantics/** --forbidden implement-plan.md IDEA.md docs/tasks/planning-to-dispatch-integration.md","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 git diff --check eb52c41..HEAD -- pipeline_tools/planning.py tests/test_planning_dispatch_integration.py tests/test_planning_lifecycle.py","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/dispatch-fail-closed-and-approval-semantics/executor-result.json --task-id dispatch-fail-closed-and-approval-semantics --role executor","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools freshness . .pipeline/dispatch-fail-closed-and-approval-semantics --result .pipeline/dispatch-fail-closed-and-approval-semantics/executor-result.json","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 DISABLE_AUTO_METRICS=1 python -m pipeline_tools evidence readiness . --task-id dispatch-fail-closed-and-approval-semantics","exit_code":0,"evidence_ref":".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md"}],"assertions":["six focused frozen acceptance tests pass independently","full regression passes with 131 tests","same/different/hash-drift task-sheet conflicts fail closed and preserve artifacts","automatic approval does not require explicit approve","manual approval blocks before worktree creation and proceeds only after approve","audit artifacts and no-worktree-on-blocked behavior are preserved","task validate, current-HEAD preflight, freeze-check, scope, diff, result verify, and freshness pass","evidence readiness is genuinely not ready because final-check.md is absent"],"evidence_refs":[".pipeline/dispatch-fail-closed-and-approval-semantics/review-report.md",".pipeline/dispatch-fail-closed-and-approval-semantics/reviewer-result.json"],"unverified":[],"identity":{"head":"fe70cbe5be815f052d7aeeca90508cc5995dad3","branch":"dispatch-fail-closed-and-approval-semantics","worktree":"D:/Projects/Skills/pipeline/.worktrees/dispatch-fail-closed-and-approval-semantics","contract":"eb52c41957e0fb81b9f95a60dfc30fb94fab53c9"},"recommendation":"PASS"}
```
