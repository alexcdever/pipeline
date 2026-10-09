# Final check

主代理最终检查（第三层验证）。

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1 | PASS | `f138659` / `a8f963f` |
| 独立审查 | **PASS** | `ffd6d70` |
| 主代理最终检查（本轮） | PASS | 本文件 |

## 本任务修的缺陷

`_read_evidence_block`（`pipeline_tools/planning.py`）原先要求起始围栏之后的**全部**围栏行恰好只有一条，于是"机器块之后正文还有别的 fenced 代码块"的报告读不出来 → 最终化报 `invalid <report>`；而闸门侧读取器能容忍同一份报告。修法：取起始围栏之后的**第一条**围栏行作为块边界，起始围栏必须恰好一条，找不到收尾围栏或 JSON 非法仍拒绝。

## 本轮主代理亲自做的事

1. **身份核对**：任务分支 `238f367 → f138659 → a8f963f → ffd6d70`；主工作树未被动过。
2. **重跑三条验收**：逐条退出码 0。
3. **重跑全量测试**：`398 passed, 28 subtests passed`，退出码 0（基线 395 + 3）。
4. **独立复验块边界**：自建夹具——机器块在前、正文另有 2 个代码块 → 解析成功（11 键）；缺起始围栏 / 缺收尾围栏 / JSON 非法 → 一律拒绝。
5. **范围与历史完好**：`238f367..f138659` 仅 3 个路径（`planning.py`、`merge-and-recovery.md`、`test_planning.py`），`.pipeline/**` 下既有报告**零改写**；禁止路径零改动；`compileall` 与 `git diff --check` 为 0。
6. **真实文件只读复核**（审查与执行者均完成）：主工作树里 T1 与 `post-merge-evidence-identity` 的四份报告，旧读取器 `None`、新读取器正常、闸门读取器一致，报告字节未变。

## 交付意义

这是最后一道堵住两条已合并任务最终化的读取器缺陷。本任务合并后，`task-sheet-revision-and-evidence-binding` 与 `post-merge-evidence-identity` 应当可以完成最终化与 `--phase finalized` 校验。

## 未验证项

- 合并后主工作树复验未进行；两条被堵任务的最终化在本任务合并后由主代理执行。
- **已记录**：`evidence-finalize` 会删除证据目录里的非保留文件，包括未跟踪的本地状态文件 `goal.json` 与 `amendments.json`；对带修订链的任务（`post-merge-evidence-identity`，revision 4）这会破坏其修订记录。主代理在最终化后从备份恢复这两个本地文件。

## 结论

三层验证全部通过，范围与历史完好。**READY-TO-MERGE。**

```pipeline-evidence
{"schema": 2, "task_id": "finalization-report-reader", "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "branch": "finalization-report-reader", "role": "main-final", "round": 1, "status": "PASS", "head": "f138659f61e7d5e47e84138b3ee4d69b064d9a87", "sheet_revision": 1, "sheet_sha256": "7e8c6a5fb3ce0add707100e484c9dc6b022c58c50dc7a67852a5f41bdeceb4f1", "observed_at_commit": "f138659f61e7d5e47e84138b3ee4d69b064d9a87", "generated_at": "2026-10-09T02:15:22Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_accepts_fences_after_the_machine_block", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_still_rejects_malformed_blocks", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_and_gate_readers_agree_on_the_same_report", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check 238f367..f138659", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all three contract acceptance commands re-run by the main agent at implementation head f138659 with exit code 0", "main agent full suite re-run: 398 passed, 28 subtests passed, exit code 0", "the main agent independently reproduced the block boundary: a machine block followed by two further code fences parses to an eleven-key object, while a missing opening fence, a missing closing fence and invalid JSON are all rejected", "three changed paths, none under .pipeline, so no existing report was rewritten; zero forbidden-path changes", "compileall exit code 0 and git diff --check exit code 0 over the implementation range"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["post-merge main-worktree re-verification pending", "the two blocked tasks were only compared read-only; their finalization runs after this task merges"]}
```
