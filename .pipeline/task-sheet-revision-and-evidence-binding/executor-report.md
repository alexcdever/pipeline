# Executor report

```pipeline-evidence
{"schema":2,"task_id":"task-sheet-revision-and-evidence-binding","worktree":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","branch":"task-sheet-revision-and-evidence-binding","role":"executor","round":2,"status":"PASS","head":"45be2dbac64d1af49bcbdb8e385e72ac87c17a11","generated_at":"2026-10-08T10:09:34Z","sheet_revision":1,"sheet_sha256":"a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783","observed_at_commit":"45be2dbac64d1af49bcbdb8e385e72ac87c17a11","commands":[{"command":"python -m pipeline_tools task validate docs/tasks/task-sheet-revision-and-evidence-binding.md","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"SKILL.md version temporarily set to 0.15.0, then: python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":1,"expected_exit_code":1,"evidence_ref":"executor-report.md"},{"command":"SKILL.md restored to 0.16.0, then: python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python repro_f1.py (independent F1 harness, PYTHONPATH=<worktree>, temp git repo)","cwd":"C:/Users/alexc/AppData/Local/Temp/executor-round2-probe","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python legacy_compare.py (F4 A/B: baseline 02a71a3 code vs round-2 code on the same legacy evidence fixture)","cwd":"C:/Users/alexc/AppData/Local/Temp/executor-round2-probe","exit_code":0,"evidence_ref":"executor-report.md"}],"assertions":["all ten acceptance commands plus the full suite exit 0 on commit 45be2db","full suite: 379 passed, 28 subtests passed, exit 0 (377 before this round plus the two new regression tests)","F1: lowering the task-level required_evidence_levels from [3] to [2] is blocked without --adjudication (exit 3, no record) and accepted with one, recorded as loosened=true, verification_surface_changed=true and adjudication_ref set","F1: the floor the lifecycle reads really moves from 3 to 2 only after the adjudicated revision","F2: with SKILL.md at version 0.15.0 the documentation test fails (exit 1, '(0, 15, 0) not greater than or equal to (0, 16, 0)') and passes again after restoring 0.16.0","F4: legacy-shaped evidence (no sheet_revision/sheet_sha256/observed_at_commit) produces zero revision errors, is reported as unverified instead, and reconcile reaches the same status and the same error list with and without the binding fields","F4: baseline 02a71a3 code and round-2 code return identical status and error list for the same legacy fixture (no new errors introduced)","F4: evidence that does declare a mismatching sheet_revision is still judged stale by the new criteria"],"evidence_refs":["executor-report.md"],"unverified":["round 1 was independently reviewed as FAIL; this round fixes F1 (task-level required_evidence_levels was not treated as loosening), F2 (the skill version assertion was a format match with no force) and F4 (legacy evidence collected new errors for missing fields)","independent review of this round pending","post-merge main-worktree re-verification pending","the reviewer's F3 observation (deleting a whole operation or narrowing operations[].resources is a verification-surface change but not a loosening) is left unchanged on purpose: the contract's second criterion is an exhaustive list and widening it needs a main-agent adjudication","the schema-2 head is the implementation commit this evidence judged; the separate evidence commit moves HEAD after that observation"]}
```

## 本轮修复（对照审查提交 `ec560ba` 的 findings）

### F1 放松判据漏掉任务级 `required_evidence_levels`（已修）

- `pipeline_tools/core.py`：新增 `required_evidence_floor(contract)`（返回 `max(required_evidence_levels)`），并把 `_contract_loosened(changes)` 改为 `_contract_loosened(previous, current, changes)`，在单条 `acceptance_tests[].evidence_level` 检查之后增加任务级下限比较：`before_floor is not None and (after_floor is None or after_floor < before_floor)` 即判 `loosened = true`。下限不变或上升不算放松（`[3] → [3,2]`、`[2,3] → [3]` 都不触发）。唯一调用点 `amend_task_sheet` 已改为传入前后契约。
- 真实验证（独立脚本 `repro_f1.py`，临时 Git 仓库，`acceptance-test-1` 为 level 3、`required_evidence_levels=[3]`）：

  ```
  freeze errors: []
  revision before: 1
  lifecycle floor before: 3
  no adjudication -> blocked loosened: None exit: 3
  errors: ['loosening the contract requires --adjudication']
  record exists: False
  with adjudication -> pass loosened: True surface: True
  delta: {'added': [2], 'removed': [3]}
  lifecycle floor after: 2
  ```
- 回归用例 `tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_loosening_covers_the_task_level_evidence_floor`：冻结 `[3]` 契约 → 下调到 `[2]` 无裁决被拒（无记录、文件未变）→ 补 `--adjudication` 后接受、`loosened=true`、`changes.required_evidence_levels == {"added": [2], "removed": [3]}`，并用 `task_lifecycle` 公开接口证明证据下限确实从 3 降到 2（仅在登记裁决之后）。
- 文档同步：`README.md`、`SKILL.md`、`templates/task-sheet.md`、`references/task-design.md`、`references/execution-and-review.md` 的「判据二」都补上任务级下限口径。

### F2 版本号断言无保证（已修）

- `tests/test_acceptance_id_and_template_compliance.py`：把 `assertRegex(skill, r"version: 0\.\d+\.\d+")` 换成解析 + 数值下限比较——从 `SKILL.md` 用 `^version:\s*(\d+)\.(\d+)\.(\d+)\s*$`（MULTILINE）取出三元组，`assertGreaterEqual(declared, (0, 16, 0))`。既不必每次升版本改测试，又能挡住版本回退。
- 反向实验（结果见报告 commands 的前两条非零/零条目）：

  | 变体 | 命令 | 退出码 | 观察 |
  |---|---|---|---|
  | `SKILL.md` 临时改回 `version: 0.15.0` | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | **1** | `AssertionError: (0, 15, 0) not greater than or equal to (0, 16, 0) : SKILL.md version must be at least 0.16.0 (found version: 0.15.0)` |
  | 恢复 `version: 0.16.0` | 同上 | **0** | `1 passed, 27 deselected` |

  实验后 `git diff SKILL.md` 只剩本轮那 1 行措辞改动，版本号已复原（`grep -n "^version:" SKILL.md` → `4:version: 0.16.0`）。

### F4 历史形态证据新增错误（已修）

- `pipeline_tools/core.py` 的 `evidence_revision_status`：只有声明了 `sheet_revision`（整数）的记录才进入新判据。历史形态（无该字段）的记录直接保留既有判定——`revision_bound: false`、`stale: false`、`reasons: []`，不产生任何错误，只在返回值的 `unverified` 里注明「未被修订判据覆盖」。声明了 `sheet_revision` 但没有 `observed_at_commit` 的记录同样只在 `unverified` 里注明「changed-path 判据未评估」，不再当成错误。
- `pipeline_tools/reconcile.py`：把该 `unverified` 附加到 reconcile 输出（不参与 PASS/BLOCKED 判定）。
- 回归用例 `tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_legacy_evidence_without_revision_fields_keeps_its_verdict`：历史形态记录零错误、零 stale；同一套证据在「带绑定字段」与「不带绑定字段」两种形态下 `reconcile_task` 的 `status` 与 `errors` 完全相同；而故意声明错误修订版本的记录仍被判 stale。
- 独立 A/B（用审查者同样手法：`git archive 02a71a3 pipeline_tools` 抽出基线代码，对同一历史形态夹具各跑一次 `reconcile_task`）：

  ```
  == baseline 02a71a3: status=BLOCKED
     - missing or invalid finalization.json
     - main worktree post-merge re-verification is missing
  == round-2 worktree: status=BLOCKED
     - missing or invalid finalization.json
     - main worktree post-merge re-verification is missing
  new errors introduced by the round-2 code: []
  ```
- `references/compat-and-migration.md` 的**本轮新增条目**（v0.15.0 → v0.16.0）补了兼容说明：新判据只作用于声明了 `sheet_revision` 的证据，历史证据保持既有判定且缺字段本身不产生错误；历史版本条目原文未改。

### F3（未修，按指示保留）

删除整个 operation、收窄 `operations[].resources` 仍只算验证面变更、不计放松。契约判据二是穷举列表，扩展需主代理裁决；本轮未改判据，已记入 `unverified`。

## 命令与结果

所有命令 cwd 详见上文 `commands`；目录内命令（前 12 条）的 cwd 是本实现 worktree 根，环境变量 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -m pipeline_tools task validate docs/tasks/task-sheet-revision-and-evidence-binding.md` | 0 | `PASS` |
| `python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence` | 0 | 1 passed |
| `python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable` | 0 | 1 passed |
| `python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening` | 0 | 1 passed |
| `python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies` | 0 | 1 passed |
| `python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze` | 0 | 1 passed |
| `python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision` | 0 | 1 passed |
| `python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only` | 0 | 1 passed |
| `python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision` | 0 | 1 passed |
| `python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role` | 0 | 1 passed |
| `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 1 passed |
| `python -m pytest -q` | 0 | 379 passed, 28 subtests passed |

## 范围

本轮只改契约 `allowed_paths` 内的文件：`pipeline_tools/core.py`、`pipeline_tools/reconcile.py`、`tests/test_task_sheet_amendment.py`、`tests/test_acceptance_id_and_template_compliance.py`、`README.md`、`SKILL.md`、`templates/task-sheet.md`、`references/{task-design,execution-and-review,compat-and-migration}.md`。未改契约的验收测试与验收 ID，未新建 worktree，未在主工作树改任何文件，未使用 `git reset`/`rebase`（本轮为追加提交）。

## 未验证

- 上一轮独立审查判 FAIL；本轮针对 F1/F2/F4 修复，尚未经过独立审查。
- 合并后主工作树复验未进行。
- F3 观察保留未修（见上）。
- 报告的 schema-2 `head` 是本轮验证的实现提交 `45be2db`；证据提交会在此之后移动 `HEAD`（只改 `.pipeline/<task-id>/`，不与任何 operation 的 `resources` 相交）。
- 文档改写的下游读者（契约 unknown-2）未经人工确认。
