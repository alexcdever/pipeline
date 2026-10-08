# Final check

主代理最终检查（第三层验证）。

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1（修 A–D） | PASS | `9f4fbcc` / `cd0f704` |
| 独立审查 round 1 | PASS，但发现 F1 | `ad2b0df` |
| 执行 round 2（收窄已合并信号） | PASS | `eae0133` / `67fc976` |
| 独立审查 round 2 | **PASS** | `b737933` |
| 主代理最终检查（本轮） | PASS | 本文件 |

## 本任务修的四件事

- **A** 最终化的报告校验原先硬性要求 `schema == 1`，导致已合并且闸门 PASS 的交付**无法最终化**；现接受 `{1,2}`。
- **B** 对账对已合并交付不再施加 active 提交绑定；已合并信号已排除 HEAD 当前所在分支（F1 修复）。
- **C** `references/merge-and-recovery.md` 中与阶段分工矛盾的旧话已删除/改写。
- **D** finalized 阶段不再要求 `observed_at_commit`；`sheet_revision` 仅在存在时判定。

端到端证据（执行者在临时仓库完成）：完整 schema 2 证据 → 合并 → `gate post-merge` PASS → `evidence-finalize` 产出 `{"status":"finalized"}` → `evidence verify --phase finalized` PASS → `evidence reconcile` PASS。**这是该链路第一次真正跑通。**

## 本轮主代理亲自做的事

1. **身份核对**：任务分支 `f07b908 → 9f4fbcc → cd0f704 → ad2b0df → eae0133 → 67fc976 → b737933`；主工作树未被动过。
2. **重跑六条验收**：逐条退出码 0。
3. **重跑全量测试**：`392 passed, 28 subtests passed`，退出码 0（基线 367）。
4. **独立复验 F1**：自建夹具直接调用 `_delivery_is_merged`——未合并且候选集含 `main` 时返回 `False`（旧判据会误判 `True`），真合并后返回 `True`。
5. **范围与卫生**：`f07b908..eae0133` 共 12 个路径，全在范围内；两个依赖任务的证据目录与任务单零改动；`compileall` 与 `git diff --check` 为 0。

## 未验证项与遗留

- 合并后主工作树复验未进行——post-merge 硬要求，合并后会重跑并更新本文件与 `final-result.json`。
- **F1-residual（低）**：detached HEAD 下没有"当前分支"可排除，宽判据仍生效；不产生假 PASS（`finalization.json` 仍必需）。
- **F2**（伪造自洽标记的信任模型边界，契约 `unknown-2` 已接受该信号）与 **F3**（`merge-and-recovery.md:47` 的 schema 1 旧表述，改动前即存在）按裁决保留现状。

## 结论

三层验证全部通过，范围与历史完好。**READY-TO-MERGE。**

```pipeline-evidence
{"schema": 2, "task_id": "finalization-and-reconcile-phase", "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "branch": "finalization-and-reconcile-phase", "role": "main-final", "round": 1, "status": "PASS", "head": "eae01331b701eb310d35bbccfd17c994b46e259b", "sheet_revision": 1, "sheet_sha256": "2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8", "observed_at_commit": "eae01331b701eb310d35bbccfd17c994b46e259b", "generated_at": "2026-10-08T23:30:57Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check f07b908..eae0133", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --name-only f07b908 eae0133", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all six contract acceptance commands re-run by the main agent at implementation head eae0133 with exit code 0", "main agent full suite re-run: 392 passed, 28 subtests passed, exit code 0", "the main agent independently reproduced the F1 fix on a fresh fixture: with main present in the branch set and the task branch unmerged, _delivery_is_merged returns False; after a real merge it returns True", "twelve changed paths between the contract baseline and the implementation all fall inside the revision 1 allowed_paths; zero forbidden-path changes including the two dependency tasks' evidence directories", "compileall exit code 0 and git diff --check exit code 0 over the implementation range"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["post-merge main-worktree re-verification pending", "F1-residual: with a detached HEAD there is no current branch to exclude, so the wider signal still applies; no false pass is possible because finalization.json remains required", "F2 and F3 are recorded and intentionally left unchanged"]}
```
