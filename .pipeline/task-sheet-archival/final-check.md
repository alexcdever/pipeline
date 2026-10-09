# Final check

主代理最终检查（第三层验证）。

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1 | PASS | `1f9e4d8` / `e22b6c1` |
| **裁决**：归档步骤为显式步骤（rev 1→2） | — | `1bd5522` |
| 执行 round 2（重出证据） | PASS | `929ba6e` |
| 独立审查 | **PASS**（40/40 自建断言） | `c4e1784` |
| 主代理最终检查（本轮） | PASS | 本文件 |

## 本任务建立的机制

1. **三位置解析**（`docs/tasks/<id>.md` → `.pipeline/<id>/<id>.md` → `.pipeline/archive/<id>.md`），多处存在或三处皆无一律报错。
2. **场景判定按状态**：工作清单只用 `docs/tasks/` 下的单子，终态单子不再产生 `sheets_without_worktree` 警告；而 `worktrees_without_sheet` 仍接受归档位置的单子。
3. **`.pipeline/archive` 不是任务证据**（加入排除集合，不会变成叫 archive 的任务）。
4. **保留集与闸门豁免**：任务的保留名包含它自己的单子；`archive/` 下的路径豁免保留名规则；反向情形仍判违规。
5. **归档步骤（显式）**：`archive_task_sheet()` 用 `git mv` 把单子移入证据目录（无证据目录时退到 `archive/`）；worktree 仍在则 blocked 且不移动；幂等。
6. **证据字节稳定**：`.gitattributes` 追加 `.pipeline/** -text`，属性提交本身不改写任何既有 blob。

## 本轮主代理亲自做的事

1. **重跑八条验收**：逐条退出码 0。
2. **重跑全量测试**：`395 passed, 30 subtests passed`，退出码 0（基线 388/30）。
3. **独立复现字节稳定**：临时仓库里以 CRLF 写入 `.pipeline` 下的证据并提交 → blob 保留 CR；新检出字节与提交时一致。
4. **范围核对**：12 个变更路径全在 revision 2 范围内；禁止路径零改动；无历史任务单/证据目录/最终化标记被移动或改写。

## 必须处置的合入事项

独立审查发现：主工作树里 **7 个已关闭任务的 `finalization.json`** 工作区为 CRLF、blob 为 LF。属性合入后它们会显示为 ` M `；**绝不可 `git add` 它们**（那会把 blob 由 LF 改写为 CRLF，触及已关闭任务的证据）。按审查建议，合入后在主工作树执行 `git checkout -- .pipeline` 让工作区回到 blob 的 LF——**只改工作区，不改任何 blob**。

## 未验证项与遗留

- 三条非阻塞审查发现：契约观察（本任务单自身字面匹配 `forbidden_paths` 的 `docs/tasks/*.md`，其改动来自主代理修订提交，实现提交未触及任何 forbidden 路径）；修订链未纳入 Git（本 worktree 内 `task_sheet_revision` 读作 1，post-merge 在主工作树执行时读作 2）；`is_archived_sheet_path` 的豁免不随扫描根收窄（当前无实际影响）。

## 结论

三层验证全部通过，范围与历史完好。**READY-TO-MERGE。**

```pipeline-evidence
{"schema": 2, "task_id": "task-sheet-archival", "worktree": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "branch": "task-sheet-archival", "role": "main-final", "round": 1, "status": "PASS", "head": "c4e17846d8daf95f744ed847e5b0b9a97428c20a", "sheet_revision": 2, "sheet_sha256": "5f3c92d875e6b03d8fd6a4f314b5c3e6f2e5d7f80786493f15b52370a0040d54", "observed_at_commit": "c4e17846d8daf95f744ed847e5b0b9a97428c20a", "generated_at": "2026-10-09T06:08:51Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k sheet_resolver_finds_all_three_locations", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k worklist_checks_ignore_terminal_sheets", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k archive_directory_is_not_treated_as_task_evidence", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k archived_sheet_still_answers_worktree_without_sheet", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_moves_the_sheet_and_refuses_while_the_worktree_lives", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k task_sheet_and_archive_are_exempt_from_the_retained_name_rule", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k pipeline_evidence_bytes_survive_a_checkout", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check 124cef5..1f9e4d8", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all eight contract acceptance commands re-run by the main agent at contract revision 2 with exit code 0", "main agent full suite re-run: 395 passed, 30 subtests passed, exit code 0", "the main agent reproduced byte stability independently: with .pipeline declared non-text the committed blob keeps its carriage returns and a fresh clone reads identical bytes", "twelve changed paths, all inside the revision 2 allowed_paths; zero forbidden-path changes, and no historical sheet, evidence directory or finalization marker was moved or rewritten", "the archival step is an explicit closure step refusing while the worktree exists, which is the adjudicated trigger recorded in revision 2"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["post-merge main-worktree re-verification pending", "seven finalization markers in the main worktree have CRLF working-tree bytes against LF blobs; after the merge they must be restored from the index so their blobs stay untouched"]}
```
