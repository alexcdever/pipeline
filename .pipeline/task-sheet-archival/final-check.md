# Final check

主代理最终检查，**合并后版本**。本文件在合并后于主工作树内重写并重跑，作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`49e3c35d57ee84a2c540dd879e5baf16bba6cc85`（`merge task sheet archival`），父提交 `1bd5522`（main）与 `8381070`（任务分支尖端）
- 主工作树根：`D:/Projects/Skills/pipeline`

## 交付意义

任务单归档机制落地：三位置统一解析、工作清单按状态判定（终态单子不再产生"单子无 worktree"警告）、`.pipeline/archive` 作为隔离区不被当成任务、保留集接纳任务自有单子且 `archive/` 豁免闸门、显式归档步骤（活 worktree 时拒绝）、`.pipeline/**` 声明为非文本以便证据字节稳定。

**本轮特别处置**：独立审查预先指出主工作树里有 7 个已关闭任务的 `finalization.json` 工作区为 CRLF、blob 为 LF，属性合入后可能被 `git add` 改写 blob。实测合并本身已把工作区从索引重新物化，`git status` 无任何已跟踪改动——**没有任何 blob 被改写**，`git checkout -- .pipeline` 为空操作。

## 合并后本人在主工作树根重跑的内容

1. 八条契约验收测试：逐条退出码 0。
2. 全量测试：`395 passed, 30 subtests passed`，退出码 0。
3. `compileall` 退出码 0；`git status` 无已跟踪改动。
4. 23 个任务目录的 `finalization.json` 完好。

## 未验证项与遗留

- 本任务自己的任务单将在收尾窗口之后作为该机制的首次实际使用被归档（先移除 worktree，再 `git mv` 进证据目录）。
- 三条非阻塞审查发现已登记（契约观察、修订链未纳入 Git、`is_archived_sheet_path` 豁免范围）。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "task-sheet-archival", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 2, "status": "PASS", "head": "49e3c35d57ee84a2c540dd879e5baf16bba6cc85", "sheet_revision": 2, "sheet_sha256": "5f3c92d875e6b03d8fd6a4f314b5c3e6f2e5d7f80786493f15b52370a0040d54", "observed_at_commit": "49e3c35d57ee84a2c540dd879e5baf16bba6cc85", "generated_at": "2026-10-09T06:15:47Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k sheet_resolver_finds_all_three_locations", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k worklist_checks_ignore_terminal_sheets", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k archive_directory_is_not_treated_as_task_evidence", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k archived_sheet_still_answers_worktree_without_sheet", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_moves_the_sheet_and_refuses_while_the_worktree_lives", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k task_sheet_and_archive_are_exempt_from_the_retained_name_rule", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k pipeline_evidence_bytes_survive_a_checkout", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git status --short", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref 8381070 into main", "all eight contract acceptance commands pass in the main worktree with exit code 0", "main worktree full suite passes: 395 passed, 30 subtests passed, exit code 0", "after the merge the working tree carries no tracked modification, so the .pipeline/** -text addition rewrote no existing blob", "twenty-three task directories still hold an intact finalization marker", "the merge is a real merge commit with parents 1bd5522 and 8381070"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker written in a following step", "the archival step is applied to this task's own sheet after the closure window, as the mechanism's first real use"]}
```
