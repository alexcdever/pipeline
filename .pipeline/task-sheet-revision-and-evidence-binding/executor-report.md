# Executor report

```pipeline-evidence
{"schema":2,"task_id":"task-sheet-revision-and-evidence-binding","worktree":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","branch":"task-sheet-revision-and-evidence-binding","role":"executor","round":1,"status":"PASS","head":"753f0a6aca79bf1de80a241dc2c5277636a795a3","generated_at":"2026-10-08T09:24:54Z","sheet_revision":1,"sheet_sha256":"a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783","observed_at_commit":"753f0a6aca79bf1de80a241dc2c5277636a795a3","commands":[{"command":"python -m pipeline_tools task validate docs/tasks/task-sheet-revision-and-evidence-binding.md","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pytest -q","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"executor-report.md"}],"assertions":["all ten acceptance commands plus the full suite exit 0 on commit 753f0a6","a recorded amendment is accepted after executor evidence and reuses the same implementation worktree and evidence directory","identity fields (schema, task_id, task_type, derived_from) are rejected, while dependencies may be added and removed with a reason only","verification-surface change and loosening are classified independently and recorded side by side","missing and cyclic dependencies are rejected with no record, no hash change and no moved file","an unrecorded task sheet edit still reports task sheet changed after freeze","evidence validity tracks the sheet revision and the verified operation resources, so HEAD moving on its own does not invalidate it","the amendment record is append-only: the previously written revision line stays byte-identical","the plan/contract consistency check reports a post-planning revision instead of a bare drift error","task amend requires role=main-agent and an adjudication reference for loosening","documentation and template describe the versioned revision model and the skill version is bumped"],"evidence_refs":["executor-report.md"],"unverified":["independent review pending","post-merge main-worktree re-verification pending","the schema-2 head is the implementation commit this evidence judged; the separate evidence commit moves HEAD after that observation"]}
```

## 交付内容

- 新增 `pipeline_tools task amend`：只做校验、分类与登记，不生成也不重写任务单内容。强制 `role=main-agent`；放松约束（删除或放宽验收测试、降低某条 `evidence_level`、改写 `test_ref`/`command_ref`、扩大 `allowed_paths`、收窄 `forbidden_paths`、删除非目标）必须带 `--adjudication`；身份字段 `schema`/`task_id`/`task_type`/`derived_from` 不可修订；`dependencies` 增删只需理由但要校验依赖任务单存在（`docs/tasks/<id>.md` → `.pipeline/<id>/<id>.md` → `.pipeline/archive/<id>.md`）且依赖图无环。退出码：接受 0、参数或契约结构错误 2、被拒绝 3。
- `pipeline_tools/core.py` 新增修订引擎：两个正交判据（`verification_surface_changed`、`loosened`）、追加式记录写入器（单行 JSON 记录、原子替换）、`task_sheet_revision`/`task_sheet_baseline_sha256`/`recorded_task_sheet_hashes`、`evidence_revision_status`（修订版本 + 被验证路径两判据）。
- `freeze_check` 改用最新修订版哈希为基准；lifecycle 的 `task_sheet_sha256` 漂移检查与身份比较也接受已登记的修订，但未登记的改动仍然漂移。
- `planning.compare_task_plan_contract` 以最新修订版为基准，依赖在规划后被修订时报告 `revised_after_planning` 而不是裸漂移。
- `reconcile` 输出 `sheet_revision`/`sheet_sha256`/`evidence_validity` 并纳入 PASS 判定；`freshness` 在结果只记录 `observed_at_commit` 时按同一路径判据判定。
- 模板与文档对齐版本化修订模型：`templates/task-sheet.md`、`templates/pipeline-evidence.json`（新增 `sheet_revision`/`sheet_sha256`/`observed_at_commit`）、`SKILL.md`（版本升到 0.16.0）、`README.md`、`references/{task-design,acceptance-evidence,execution-and-review,merge-and-recovery,compat-and-migration}.md`。`references/execution-and-review.md` 保留“执行/审查子代理不得改任务单”的约束，并补上“发现契约缺陷时提交结构化反馈给主代理”。`references/compat-and-migration.md` 只新增 v0.15.0 → v0.16.0 条目，历史条目原文未改。
- 测试：新增 `tests/test_task_sheet_amendment.py`（9 个用例，覆盖 8 条任务单验收测试、reconcile 绑定与 lifecycle 修订基准）；`tests/test_acceptance_id_and_template_compliance.py` 的文档措辞断言改为描述“冻结 + 版本化修订 + 身份字段不可修订”，技能版本号断言改为模式匹配。

## 命令与结果

所有命令的 cwd 都是本实现 worktree 根目录，环境变量 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

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
| `python -m pytest -q` | 0 | 377 passed, 28 subtests passed |

## 未验证

- 独立审查（reviewer 子代理）尚未进行。
- 合并后主工作树复验尚未进行。
- 报告的 schema-2 `head` 是本轮实际验证的实现提交 `753f0a6`；证据提交会在此之后移动 `HEAD`（只改 `.pipeline/<task-id>/`，不与任何 operation 的 `resources` 相交）。
- 文档改写的下游读者（是否有其它消费者依赖被改写段落的旧措辞）未经人工确认。
