# Final check

主代理最终检查，**合并后版本**。本文件在合并后于主工作树内重写并重跑，作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`b48e7502d04f7bcaf02d27a14fd264a5c384510b`（`merge finalization report reader`），父提交 `238f367`（main）与 `713ecf8`（任务分支尖端）
- 主工作树根：`D:/Projects/Skills/pipeline`

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1 | PASS | `f138659` / `a8f963f` |
| 独立审查 | **PASS**（37/37 条独立断言） | `ffd6d70` |
| 主代理最终检查（合并前） | PASS，pre-merge 闸门通过 | `713ecf8` |
| 主代理最终检查（合并后，本轮） | PASS | 本文件 |

## 交付意义

这是最后一道堵住两条已合并任务最终化的读取器缺陷：`_read_evidence_block` 原先要求"全文件剩余部分只有一个收尾围栏"，于是正文在机器块之后还有代码块的报告读不出来。修复后，`task-sheet-revision-and-evidence-binding` 与 `post-merge-evidence-identity` 的报告可被两个读取器一致读出，据执行者与审查者的只读复验与副本演练，最终化不再报 `invalid`。

## 合并后本人在主工作树根重跑的内容

1. 三条契约验收测试：逐条退出码 0。
2. 全量测试：`398 passed, 28 subtests passed`，退出码 0（基线 367）。
3. 依赖可加载；`compileall` 与 `git diff --check` 退出码 0。

## 未验证项

- 本文件提交后才会写入最终化标记，随后执行 `evidence verify --phase finalized`。
- **已记录**：`evidence-finalize` 会删除证据目录里的非保留文件（含未跟踪的 `goal.json` 与 `amendments.json`）；主代理在最终化后从备份恢复这两个本地文件，以保住带修订链任务的修订记录。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "finalization-report-reader", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 2, "status": "PASS", "head": "b48e7502d04f7bcaf02d27a14fd264a5c384510b", "sheet_revision": 1, "sheet_sha256": "7e8c6a5fb3ce0add707100e484c9dc6b022c58c50dc7a67852a5f41bdeceb4f1", "observed_at_commit": "b48e7502d04f7bcaf02d27a14fd264a5c384510b", "generated_at": "2026-10-09T02:21:07Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_accepts_fences_after_the_machine_block", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_still_rejects_malformed_blocks", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_and_gate_readers_agree_on_the_same_report", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -c \"import pipeline_tools.planning, pipeline_tools.core; print('imports ok')\"", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check 238f367..HEAD", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref 713ecf8 into main", "all three contract acceptance commands pass in the main worktree with exit code 0", "main worktree full suite passes: 398 passed, 28 subtests passed, exit code 0", "pipeline_tools modules import cleanly; compileall exit code 0; git diff --check exit code 0", "the merge is a real merge commit with parents 238f367 and 713ecf8", "no existing report was rewritten by this delivery; only the reader changed"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker written in a following step", "evidence-finalize deletes the local state files goal.json and amendments.json; the main agent restores them afterwards for the tasks that carry a revision chain"]}
```
