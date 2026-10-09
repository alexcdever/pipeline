# Final check

主代理最终检查，**合并前版本**。本文在任务 worktree 内写就；合并后会在主工作树重写并重跑，作为独立 post-merge 证据提交。

## 任务信息

- task-id：`historical-archival-migration`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration`
- branch：`historical-archival-migration`
- 被检 HEAD：`c81330a63f6d26166aaab56e23219063c943329e`
- 契约：rev 2，`sheet_sha256 = 4b43c666817ffeaa4d4518addc65524b448469aba88498c0dc5e5684c06ed497`
- 基线：`de5c6c87225bcfcd094dbc6b5d452f82feb8625c`

## 交付意义

`docs/tasks/` 里 46 张终态任务单被迁出：44 张按其**声明 id** 归入 `.pipeline/<声明 id>/<声明 id>.md`，2 张无证据目录的归入 `.pipeline/archive/`。两张在途单（本任务自身、`security-scan-repair-20261001`）留在原处。`docs/tasks/` 现只剩这两张，`planning preflight` 不再报"遗留证据目录"与"单子无 worktree"（主工作树视角）。文件名与声明 id 不符的唯一一张（`docs/tasks/repository-evidence-hygiene.md`，声明 id `repository-evidence-hygiene-continuation-5`）按其声明 id 归位到已存在的证据目录，字节不变；因此不需要任何合成的历史说明单。

## 本人（主代理）在本 worktree 重跑的内容

1. 五条契约验收测试：逐条退出码 0（见下方 commands）。
2. 全量测试：`399 passed, 30 subtests passed`，退出码 0。
3. 字节不变抽样：`pipeline-tools-v1`、`status-vocabulary-unification`、`task-sheet-archival`、`repository-evidence-hygiene-continuation-5`（改名归位）与两张 archive 单，迁移前后 sha256 全部相同。
4. `scope check`：改动全部落在契约 `allowed_paths` 内，退出码 0。
5. `planning preflight`：`leftover_evidence` 与 `worktrees_without_sheet` 均为空，无幻影单 `README`。

## 独立审查

审查子代理以独立上下文复验：五条验收真实退出码 0；抽样 7 张哈希 7/7 一致，且 `git diff -M` 显示 46 条迁移全部 `R100`；对 5 处机制做定点变异，对应用例真实 FAILED，证明断言非恒真；遍历 24 个 `finalization.json`，保留集失配 0 例。结论 PASS。

## 未验证项与遗留

- 46 张单未逐张人工复算，但全量 `R100` 已覆盖字节不变性。
- 契约在本次执行中由 rev 1 修订到 rev 2（`verification_surface_changed=true`，`loosened=true`）：按声明 id 归档、不新增 `docs/tasks/README.md`、`tests/test_cli.py` 并入可改范围。旧轮证据已作废并按新修订重做。
- 迁移后仍留在 `docs/tasks/` 的两张在途单对应的、以及已终态任务遗留的 `.worktrees/**`，由主代理在本任务合并后另行维护，不属本任务范围。

## 结论

worktree 通过，契约验收与全量回归全绿，审查独立通过。**ready-to-merge。**

```pipeline-evidence
{"schema": 2, "task_id": "historical-archival-migration", "worktree": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "branch": "historical-archival-migration", "role": "main-final", "round": 1, "status": "PASS", "head": "c81330a63f6d26166aaab56e23219063c943329e", "sheet_revision": 2, "sheet_sha256": "4b43c666817ffeaa4d4518addc65524b448469aba88498c0dc5e5684c06ed497", "observed_at_commit": "c81330a63f6d26166aaab56e23219063c943329e", "generated_at": "2026-10-09T07:37:35Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pipeline_tools planning preflight .", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all five contract acceptance commands pass in the task worktree with exit code 0", "the task worktree full suite passes: 399 passed, 30 subtests passed, exit code 0", "sampled migrated sheets are byte-identical to their pre-migration blobs at the baseline commit", "scope check reports no change outside the contract allowed_paths", "planning preflight reports empty leftover_evidence and worktrees_without_sheet with no phantom README sheet", "the independent reviewer re-ran the acceptance tests, re-computed hashes and used mutation checks to prove the assertions are not vacuous"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["post-merge re-verification is pending in the main worktree", "stale task worktrees may be removed by the main agent after this task merges"]}
```
