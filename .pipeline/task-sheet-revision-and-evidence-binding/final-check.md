# Final check

主代理最终检查，round 3（**合并后版本**）。本文件在合并后于主工作树内重写并重跑，按项目规则作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`cec0c5828df080c4b7f2e995cb485ae9a970652b`（`merge task sheet revision and evidence binding`），父提交 `02a71a3`（main）与 `c25aea4`（任务分支尖端）
- 合并输入：经 `git worktree list --porcelain` 确认过的 branch ref `task-sheet-revision-and-evidence-binding`
- 主工作树根：`D:/Projects/Skills/pipeline`

## 三层验证经过（合并前）

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行子代理 round 1 | PASS | `e525d80` |
| 独立审查 round 1 | **FAIL** | `ec560ba` |
| 执行子代理 round 2（修 F1/F2/F4） | PASS | `45be2db` / `5de6c48` |
| 独立审查 round 2 | PASS | `0b57932` |
| 主代理最终检查 round 1 → `gate pre-merge` **失败** | FAIL | `6459d33` |
| 执行子代理 round 3（修 G1/G3） | PASS | `b5a1d14` / `d946136` |
| 独立审查 round 3 | PASS | `6c3fa45` |
| 主代理最终检查 round 2 → `gate pre-merge` **PASS** | PASS | `c25aea4` |

两次失败都是真实缺陷、不是流程噪声：round 1 审查发现放松判据漏掉任务级证据下限（可把下限从 3 降到 2 而无需裁决）；主代理 round 1 最终检查发现 `evidence_verify` 仍要求 schema-2 报告的 `head` 与当前 HEAD 严格相等，导致报告提交后自判失效——正是本任务要消灭的记账循环。

## 合并后本人在主工作树根重跑的内容

1. 十条契约验收测试：逐条退出码 0。
2. 全量测试：`380 passed, 28 subtests passed`，退出码 0（基线 367）。
3. 依赖可加载：`pipeline_tools` 五个模块 import 正常。
4. `compileall` 退出码 0；`git diff --check 02a71a3..HEAD` 退出码 0。
5. 变更范围：22 个文件，全部落在契约 `allowed_paths` 内；`forbidden_paths` 零改动。

## 未验证项与已记录观察

- **O1**：绑定修订但缺 `observed_at_commit` 的证据不执行路径判据，仅在 `reconcile.unverified` 提示，属有意兼容设计。
- **O3**：本任务单未被修订（revision 1）；`goal.json` 为本地冻结记录，按仓库约定不入 Git。
- **F3**：删除整个 operation 或收窄 `operations[].resources` 只算验证面变更、不计为放松；契约判据二是穷举清单，本轮有意不改，登记为已知项。
- 遗留：`.worktrees/task-sheet-revision-and-evidence-binding` 与另外两个历史 worktree 的清理交给后续的归档任务（T4），本任务不做。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "task-sheet-revision-and-evidence-binding", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 3, "status": "PASS", "head": "cec0c5828df080c4b7f2e995cb485ae9a970652b", "sheet_revision": 1, "sheet_sha256": "a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783", "generated_at": "2026-10-08T11:36:10Z", "commands": [{"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -c \"import pipeline_tools, pipeline_tools.core, pipeline_tools.planning, pipeline_tools.task_lifecycle, pipeline_tools.reconcile; print('imports ok')\"", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check 02a71a3..HEAD", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref c25aea4 into main", "all ten contract acceptance commands pass in the main worktree with exit code 0", "main worktree full suite passes: 380 passed, 28 subtests passed, exit code 0", "pipeline_tools modules import cleanly in the main worktree; compileall exit code 0; git diff --check exit code 0", "merge is a real merge commit with parents 02a71a3 and c25aea4", "no post-merge-only failure: the merged product behaves identically to the branch tip"], "evidence_refs": ["final-check.md", "final-result.json"], "unverified": ["O1: revision-bound evidence without observed_at_commit is only surfaced as unverified", "O3: this task carries no amendment record, so only the revision number can be compared", "F3 is a recorded bounded observation left unchanged on purpose"]}
```
