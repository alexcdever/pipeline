# Final check

主代理最终检查，**合并后版本**。本文件在合并后于主工作树内重写并重跑，作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`5246beaeca4a7c9e6444b44b9c2910f1c6d53930`（`merge finalization and reconcile phase`），父提交 `f07b908`（main）与 `fe75b02`（任务分支尖端）
- 主工作树根：`D:/Projects/Skills/pipeline`

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1（修 A–D） | PASS | `9f4fbcc` / `cd0f704` |
| 独立审查 round 1 | PASS，发现 F1 | `ad2b0df` |
| 执行 round 2（收窄已合并信号） | PASS | `eae0133` / `67fc976` |
| 独立审查 round 2 | **PASS** | `b737933` |
| 主代理最终检查（合并前） | PASS，pre-merge 闸门通过 | `fe75b02` |
| 主代理最终检查（合并后，本轮） | PASS | 本文件 |

## 合并后本人在主工作树根重跑的内容

1. 六条契约验收测试：逐条退出码 0。
2. 全量测试：`392 passed, 28 subtests passed`，退出码 0（基线 367）。
3. 依赖可加载；`compileall` 与 `git diff --check` 退出码 0。
4. 独立复验 F1：自建夹具直接调用 `_delivery_is_merged`——未合并且候选集含 HEAD 当前分支时返回 `False`，真合并后返回 `True`。

## 交付意义

`evidence-finalize` 在此之前对任何 schema 2 报告一律判 `invalid`，**所有现代任务都无法最终化**；本任务修好 A 之后，最终化链路第一次跑通（执行者在临时仓库端到端演示：合并 → post-merge 闸门 PASS → `evidence-finalize` 产出 `finalized` → `--phase finalized` PASS → `reconcile` PASS）。B 的对账阶段感知与 F1 的收窄使已合并交付能通过对账，而未合并任务仍施加完整提交绑定。

## 未验证项

- 本文件提交后才会写入最终化标记（`finalization.json`），随后执行 `evidence verify --phase finalized`。
- **F1-residual（低）**：detached HEAD 下无当前分支可排除，宽判据仍生效；不产生假 PASS。
- **F2**、**F3** 按裁决保留现状。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "finalization-and-reconcile-phase", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 2, "status": "PASS", "head": "5246beaeca4a7c9e6444b44b9c2910f1c6d53930", "sheet_revision": 1, "sheet_sha256": "2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8", "observed_at_commit": "5246beaeca4a7c9e6444b44b9c2910f1c6d53930", "generated_at": "2026-10-08T23:40:40Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -c \"import pipeline_tools.core, pipeline_tools.reconcile, pipeline_tools.planning, pipeline_tools.task_lifecycle; print('imports ok')\"", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check f07b908..HEAD", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref fe75b02 into main", "all six contract acceptance commands pass in the main worktree with exit code 0", "main worktree full suite passes: 392 passed, 28 subtests passed, exit code 0", "pipeline_tools modules import cleanly; compileall exit code 0; git diff --check exit code 0", "the merge is a real merge commit with parents f07b908 and fe75b02", "this delivery is what makes finalization possible again: before it, evidence-finalize rejected every schema 2 report"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker written in a following step", "F1-residual under detached HEAD", "F2 and F3 intentionally left unchanged"]}
```
