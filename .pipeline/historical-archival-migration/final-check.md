# Final check

主代理最终检查，**合并后版本**。本文件在合并后于主工作树内重写并重跑，作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`ff7699e29953c64507e59974bdd1771c422a3f27`（`merge historical archival migration`），父提交 `28e166c`（main）与 `77ea185`（任务分支尖端）
- 主工作树根：`D:/Projects/Skills/pipeline`
- 契约：rev 2，`sheet_sha256 = 4b43c666817ffeaa4d4518addc65524b448469aba88498c0dc5e5684c06ed497`

## 交付意义

`docs/tasks/` 里 46 张终态任务单被迁出：44 张按其**声明 id** 归入 `.pipeline/<声明 id>/<声明 id>.md`，2 张无证据目录的归入 `.pipeline/archive/`。两张在途单（本任务自身、`security-scan-repair-20261001`）留在原处。合并后 `docs/tasks/` 只剩这两张，`.pipeline/archive/` 只剩 `implement-plan-coverage-repair-continuation-1.md` 与 `pipeline-evidence-lifecycle-migration.md`。`planning preflight` 在主工作树**零警告**：不再报"单子无 worktree"，`leftover_evidence` 为空，`worktrees_without_sheet` 为空，且没有幻影单 `README`。

文件名与声明 id 不符的唯一一张（原 `docs/tasks/repository-evidence-hygiene.md`，声明 id `repository-evidence-hygiene-continuation-5`）按其声明 id 归位到已存在的证据目录，字节不变；因此不需要任何合成的历史说明单。`docs/tasks/README.md` 未创建（工作清单扫描把 `docs/tasks/*.md` 一律当作任务单，放 README 会产生幻影单）。

## 合并后本人在主工作树根重跑的内容

1. 五条契约验收测试：逐条退出码 0。
2. 全量测试：`399 passed, 30 subtests passed`，退出码 0。
3. `planning preflight`：`status=pass`，`warnings=[]`，`errors=[]`。

## 未验证项与遗留

- 迁移后仍留在 `docs/tasks/` 的两张在途单对应的、以及已终态任务遗留的 `.worktrees/**`，由主代理在本任务最终化之后作为独立维护动作处理，不属本任务范围。
- `docs/goal.md` 的 goal hash 未记录（本任务未改该文件）。
- 契约由 rev 1 修订到 rev 2（`verification_surface_changed=true`）：按声明 id 归档、不新增 `docs/tasks/README.md`、`tests/test_cli.py` 并入可改范围。

## 结论

worktree 通过，主工作树复验通过，审查独立通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "historical-archival-migration", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 2, "status": "PASS", "head": "ff7699e29953c64507e59974bdd1771c422a3f27", "sheet_revision": 2, "sheet_sha256": "4b43c666817ffeaa4d4518addc65524b448469aba88498c0dc5e5684c06ed497", "observed_at_commit": "ff7699e29953c64507e59974bdd1771c422a3f27", "generated_at": "2026-10-09T07:47:07Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pipeline_tools planning preflight .", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref 77ea185 into main", "all five contract acceptance commands pass in the main worktree with exit code 0", "the main worktree full suite passes: 399 passed, 30 subtests passed, exit code 0", "planning preflight reports status pass with empty warnings and errors after the merge", "docs/tasks holds only the two in-flight sheets and .pipeline/archive holds only the two sheets with no evidence directory", "the merge is a real merge commit with parents 28e166c and 77ea185"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker is written in the following step", "stale task worktrees may be removed by the main agent after this task finalizes"]}
```
