# Final check

主代理最终检查，**合并后版本**。本文件在合并后于主工作树内重写并重跑，作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`37562cc0c0a168e020121ae65ae9fc07300abcd8`（`merge finalization hygiene`），父提交 `06ff204`（main）与 `dc4abd0`（任务分支尖端）
- 主工作树根：`D:/Projects/Skills/pipeline`

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1（代码） | PASS | `f211892` / `44444ba` |
| 范围修订（revision 1→2） | — | `06ff204` |
| 执行 round 2（文档同步） | PASS | `21e8168` / `07679fc` |
| round 2 审查 | **PASS** | `4857e36` |
| 主代理最终检查（合并前） | PASS，pre-merge 闸门通过 | `dc4abd0` |
| 主代理最终检查（合并后，本轮） | PASS | 本文件 |

## 交付意义

- **最终化不再删除本地状态文件**：`goal.json` 与 `amendments.json` 被豁免，与保留集一并留下；其余过程产物照旧剪掉。此前对这五个已关闭任务，主代理只能手工从备份恢复这两个文件才关得掉带修订链的任务。
- **"仅证据提交"的范围放宽到 `.pipeline/**` 全域 + metrics**：别的任务提交证据不再让已关闭任务报 `finalization head is stale`；混合提交与不可解析路径保持 fail-closed。

## 合并后本人在主工作树根重跑的内容

1. 四条契约验收测试：逐条退出码 0。
2. 全量测试：`401 passed, 28 subtests passed`，退出码 0（基线 367）。
3. 依赖可加载；`compileall` 与 `git diff --check` 退出码 0。

## 未验证项与遗留（登记给后续文档统一）

- 两处范围外措辞残留：`references/acceptance-evidence.md:66`（`evidence_freshness` 段未点名 `.pipeline`）、`references/compat-and-migration.md:13`（历史版本条目，不重写）。
- 版本与兼容条目纪律中断（近几轮行为变更未配 `compat-and-migration.md` 条目，`SKILL.md` 仍 `0.16.0`）。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "finalization-hygiene", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 3, "status": "PASS", "head": "37562cc0c0a168e020121ae65ae9fc07300abcd8", "sheet_revision": 2, "sheet_sha256": "65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e", "observed_at_commit": "37562cc0c0a168e020121ae65ae9fc07300abcd8", "generated_at": "2026-10-09T03:15:41Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -c \"import pipeline_tools.core, pipeline_tools.planning; print('imports ok')\"", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check 06ff204..HEAD", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref dc4abd0 into main", "all four contract acceptance commands pass in the main worktree with exit code 0", "main worktree full suite passes: 401 passed, 28 subtests passed, exit code 0", "pipeline_tools modules import cleanly; compileall exit code 0; git diff --check exit code 0", "the merge is a real merge commit with parents 06ff204 and dc4abd0", "this delivery is what lets finalization stop deleting the local state files, so no manual restore is needed any more"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker written in a following step", "two residual wordings outside this contract's scope are recorded for later documentation work"]}
```
