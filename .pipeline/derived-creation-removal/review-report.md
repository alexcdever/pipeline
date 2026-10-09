# 独立审查报告（round 2）：derived-creation-removal

- 任务单：`docs/tasks/derived-creation-removal.md`，revision **3**（修订 3 = 修正 `acceptance-test-4` 的 `test_ref` 类名 `CliTests` → `CLITests`）
- 任务单 sha256：`ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal`
- branch：`derived-creation-removal`
- **产生本证据时的分支尖端（本报告 `head` 与 `observed_at_commit`）**：`d89ba7f4e9465d1d2ba4a03cb678ea4048bcb6d1`（= 提交本证据前的 `git rev-parse HEAD`）
- 待审实现提交（实现内容未变）：`b4ca1179f30b054493e0c5227bcb86f3f6602e6b`
- 契约基线（revision 2）：`cac7cfd`
- 全部复验亲自执行；只读产品代码，未改任何产品/测试/文档，未回退提交，未动主工作树或其它任务证据目录。

## 0. 本轮的修正：`head` 语义

round 1 把 `head` 记成实现提交 `b4ca117`。该提交早于 revision 2（`cac7cfd`）与 revision 3（`f1e97e8`）两次契约修订，`b4ca117..HEAD` 区间含有 `docs/tasks/derived-creation-removal.md` 的非证据改动，因此 `evidence_verify` 的「evidence-only advance」判据不可能成立，`gate pre-merge` 必然报 `head does not match current Git identity`。

修正后的语义：`head` / `observed_at_commit` 记录**产生本证据时的分支尖端**——它评判的就是当时那个状态（已含 revision 3），后续证据提交都落在它之后且只动 `.pipeline/<task-id>/**`，判据成立。本轮 `head` = `observed_at_commit` = `d89ba7f4e9465d1d2ba4a03cb678ea4048bcb6d1`。

## 1. 环境与身份

| # | 检查 | 结果 |
|---|------|------|
| 1 | `git rev-parse --show-toplevel` | PASS → `D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal` |
| 2 | `git branch --show-current` | PASS → `derived-creation-removal` |
| 3 | 产生证据时的尖端 `git rev-parse HEAD` | `d89ba7f4e9465d1d2ba4a03cb678ea4048bcb6d1` |
| 4 | `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` | PASS → 退出码 0，输出 `PASS` |
| 5 | worktree 干净（无未提交产品改动） | PASS → `git status --porcelain` 仅剩本轮待写的两份证据 |

## 2. 第 3 节各点独立观察

### 点 1 — 实现未变

`git diff b4ca1179f30b054493e0c5227bcb86f3f6602e6b HEAD -- pipeline_tools tests SKILL.md README.md references` **输出为空（`git diff --stat` 无任何行，退出码 0）**。`b4ca117..HEAD` 的全部改动路径只有 7 条，除任务单本身 `docs/tasks/derived-creation-removal.md`（revision 3）外全部落在 `.pipeline/derived-creation-removal/**`。因此 round 1 对实现行为的全部结论继续适用，无需扩大复验。

### 点 2 — 五条 `test_ref` 全部可解析

走 pipeline 自己的校验路径 `pipeline_tools.core._acceptance_test_ref_position_errors`（`core.py:1426`，`gate_check` 在 `core.py:1875` 调用它），从任务单解析出契约后运行：

| 验收 ID | 解析出的 (path, symbol) |
|---|---|
| acceptance-test-1 | `tests/test_planning.py` / `PlanningTests.test_new_task_plan_rejects_the_derived_type` |
| acceptance-test-2 | `tests/test_planning.py` / `PlanningTests.test_generated_sheets_never_declare_derived` |
| acceptance-test-3 | `tests/test_derived_task_dispatch_recovery.py` / `DerivedTaskDispatchRecoveryTests.test_historical_derived_contracts_still_validate` |
| acceptance-test-4 | `tests/test_cli.py` / `CLITests.test_dispatch_derived_create_is_no_longer_exposed` |
| acceptance-test-5 | `tests/test_acceptance_id_and_template_compliance.py` / `AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract` |

`_acceptance_test_ref_position_errors(root, contract)` 返回 **`[]`**，即 **五条全部解析成功**。`acceptance-test-4` 是 revision 3 修正的那条：`tests/test_cli.py:77` 的类名确为 `class CLITests`，而 round 1/2 的旧措辞 `CliTests` 与之不符、会报 `test_ref method is absent`——修订后该错误消失。`gate pre-merge` 输出中亦无任何 `test_ref` 相关错误。

### 点 5 — round 1 关键结论抽查（仍成立）

1. **新计划声明 `derived` 被 fail-closed 拒绝**：用 round 1 自建夹具重跑。`type: derived` → 退出码 **2**，`{"status":"fail","errors":[... "declares the derived type; new tasks are never derived - ...", ... "declares a derived-form plan (parent_task_id/derived_from); ..."]}`；`repair` + `parent_task_id` → 退出码 **2**（`derived-form plan`）。
2. **`contract.py` 逐字节未改**：`git diff cac7cfd HEAD -- pipeline_tools/contract.py | wc -l` = **0**；`contract.py:29` 仍为 `TASK_TYPES = {"vertical-feature", "prerequisite", "repair", "derived"}`。
3. **7 张含 `derived_from` 的历史单全 PASS**：`derived-creation-removal.md`、`derived-generation-support.md`、`gate-deletion-semantics-continuation-1.md`、`metrics-tracking-policy-continuation-1.md`、`security-scan-repair-20261001-continuation-1.md`、`task-design-corruption-fix.md`、`task-sheet-revision-and-evidence-binding.md` → 逐张 `task validate` 退出码 **0**、输出 `PASS`，`ALL_PASS=yes`。

## 3. 五条契约验收测试（cwd = worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）

| ID | 命令 | 退出码 | 观察 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type` | 0 | `1 passed, 53 deselected` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived` | 0 | `1 passed, 53 deselected` |
| acceptance-test-3 | `python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate` | 0 | `1 passed, 2 subtests passed` |
| acceptance-test-4 | `python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed` | 0 | `1 passed, 63 deselected` |
| acceptance-test-5 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | `1 passed, 27 deselected` |

## 4. 全量测试与其它命令

- `python -m pytest -q`（cwd = worktree 根）→ 退出码 **0**，**`388 passed, 30 subtests passed`（307.19s）**。与上几轮的 **388 / 30** **一致**。
- `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` → 退出码 **0**（PASS）。
- `python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor` → 退出码 **0**（PASS）。
- `python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed <revision allowed_paths> --forbidden <revision forbidden_paths>` → 退出码 **0**（PASS）。
- `git diff --check b4ca1179f30b054493e0c5227bcb86f3f6602e6b HEAD` → 退出码 **0**。

## 5. `gate pre-merge`

**改写本报告之前**（磁盘上是 round 1 的 `head=b4ca117`）：退出码 **3**、`status: blocked`，错误两条：

```
"review-report.md head does not match current Git identity"
"final-check.md head does not match current Git identity"
```

**改写并提交本报告之后**（见下方「改写后」）：`review-report.md` 的 head 错误**消失**；仅余 `final-check.md` 一条（主代理阶段项，属预期——它仍记 `head=b4ca117`、`sheet_revision=2`）。`gate pre-merge` 在提交本证据后因 `final-check.md` 仍非 mergeable 而整体仍 `blocked`，这是预期结果，不属于 reviewer 可修范围。提交后的实际输出记录在本报告末尾的 `commands`（`gate pre-merge` post-commit 一条，`expected_exit_code` 已声明）。

## 6. 结论与 findings

**结论：PASS。** 实现自 `b4ca117` 起未变；五条 `test_ref` 经 pipeline 自身校验路径全部解析；五条验收退出码 0；全量 388/30 与历史声明一致；round 1 的三条关键结论重验仍成立；`head` 语义已修正、`review-report.md` 的 gate head 错误消除。

findings（不阻塞，延续 round 1）：

1. **低**：`README.md:29` 把「三类」归因于 `TASK_TYPES`，而同段括注 `TASK_TYPES` 仍含 `derived`，易误读（同段已澄清，非事实错误）。
2. **低**：被删的 `test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume` 原覆盖的「失败时保留父现场」随载体函数消失而失去专用断言。
3. **极低**：`references/task-design.md` 引用的 `contract.py:131-145`/`:166` 行号微偏（实为 132-146/167），改动前即如此。

## 7. 未复验（unverified）

- 本轮**修正了 `head` 语义**：`head` / `observed_at_commit` 改记产生证据时的分支尖端（`d89ba7f`），而非早于契约修订的实现提交 `b4ca117`。
- 被移除创建路径的运行时行为无法再实际触发，只验证了「不存在」。
- `final-check.md` 仍为 `head=b4ca117`、`sheet_revision=2`，其 gate head 错误需由 final 角色在当前尖端重出证据后消除。

## 8. blockers

无。

```pipeline-evidence
{"schema": 2, "task_id": "derived-creation-removal", "worktree": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "branch": "derived-creation-removal", "role": "reviewer", "round": 2, "status": "PASS", "head": "d89ba7f4e9465d1d2ba4a03cb678ea4048bcb6d1", "sheet_revision": 3, "sheet_sha256": "ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd", "observed_at_commit": "d89ba7f4e9465d1d2ba4a03cb678ea4048bcb6d1", "generated_at": "2026-10-09T04:44:58+00:00", "commands": [{"command": "git rev-parse --show-toplevel", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git rev-parse HEAD  # branch tip at the time this evidence was produced", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git diff b4ca1179f30b054493e0c5227bcb86f3f6602e6b HEAD -- pipeline_tools tests SKILL.md README.md references", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git diff --name-only b4ca1179f30b054493e0c5227bcb86f3f6602e6b HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python - (pipeline_tools.core._acceptance_test_ref_position_errors over the five sheet test_refs)", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "sha256sum docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git diff cac7cfd HEAD -- pipeline_tools/contract.py", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json planning task-plan-validate <own derived-type plan>", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 2, "expected_exit_code": 2, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json planning task-plan-validate <own repair+parent_task_id plan>", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 2, "expected_exit_code": 2, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "for f in $(grep -rl derived_from docs/tasks/*.md); do python -m pipeline_tools task validate \"$f\"; done", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json gate pre-merge .pipeline/derived-creation-removal --task-id derived-creation-removal --branch derived-creation-removal  # before rewriting this report: review-report.md and final-check.md head mismatches", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 3, "expected_exit_code": 3, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json gate pre-merge .pipeline/derived-creation-removal --task-id derived-creation-removal --branch derived-creation-removal  # after committing this report: review-report.md head error gone, final-check.md only", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 3, "expected_exit_code": 3, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json scope check . --task-id derived-creation-removal --allowed <allowed_paths> --forbidden <forbidden_paths>", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git diff --check b4ca1179f30b054493e0c5227bcb86f3f6602e6b HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}], "assertions": ["head and observed_at_commit now record the branch tip at the time the evidence was produced (d89ba7f), not the implementation commit b4ca117, so the range to any later evidence commit contains only .pipeline paths and the evidence-only advance rule holds", "no implementation, test or documentation file changed since b4ca117: the diff over pipeline_tools, tests, SKILL.md, README.md and references is empty, and every changed path outside the task sheet is this task's evidence directory", "all five sheet test_refs resolve through pipeline_tools.core._acceptance_test_ref_position_errors, including acceptance-test-4 whose class name revision 3 corrected to CLITests", "all five contract acceptance commands exit 0 and the full suite exits 0 with 388 passed, 30 subtests passed, matching the previous rounds", "the key round 1 results still hold: a plan declaring derived is rejected fail-closed (exit 2), contract.py is byte-identical since cac7cfd with TASK_TYPES still containing derived, and all 7 historical sheets containing derived_from pass task validate", "gate pre-merge reported review-report.md and final-check.md head mismatches before this report was rewritten; after rewriting, the review-report.md mismatch is gone and only final-check.md remains as the expected main-agent item", "task validate, result verify, scope check and git diff --check all exit 0"], "evidence_refs": [".pipeline/derived-creation-removal/review-report.md", ".pipeline/derived-creation-removal/reviewer-result.json"], "unverified": ["round 2 corrects the head semantics: head and observed_at_commit name the branch tip when the evidence was produced (d89ba7f) instead of the implementation commit b4ca117, which predated the revision 2 and 3 amendments and could never satisfy the evidence-only advance rule", "the runtime behaviour of the removed creation path cannot be re-exercised because the entry point no longer exists; only its absence is verified", "final-check.md still records head b4ca117 and sheet_revision 2; its gate head mismatch remains until the final role re-produces evidence at the current tip"], "blockers": [], "recommendation": "ready_for_finalization"}
```
