# executor-report：derived-creation-removal（round 4，修正 `head` 语义）

## 任务身份

- task-id：`derived-creation-removal`
- task-type：`repair`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal`
- branch：`derived-creation-removal`
- **产生本证据时的分支尖端**：`875f4a5452b88932078b4a0f36db401604c39af1`
- 实现提交（未变）：`b4ca1179f30b054493e0c5227bcb86f3f6602e6b`
- role：executor，round **4**
- sheet_revision：**3**
- sheet_sha256：`ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd`

**实现与测试一字不动**，本轮只修正 `head`/`observed_at_commit` 的语义并重出证据。

## 本轮的修正：`head` 记录「产生证据时的分支尖端」

round 2/3 把 `head`（与 `observed_at_commit`）写成**实现提交** `b4ca117`。契约在实现提交之后被修订过两次（revision 2 加 `allowed_paths`、revision 3 改 `test_ref`），其中 revision 3 改的是 `docs/tasks/derived-creation-removal.md` ——**不在 `.pipeline/` 下**。于是 `pipeline_tools/core.py:2563` 的 `head_advanced_by_evidence_only` 判定 `b4ca117..HEAD` 为「非仅证据提交」（`evidence_only_paths` 只认 `.pipeline/**` 与 metrics 路径），`gate pre-merge` 报 `head does not match current Git identity`。

修正后的语义：`head` 记录**这份证据评判的是哪个状态**，即产生证据时的分支尖端。该尖端已经包含契约修订，因此后续每条证据提交都落在它之后且只动 `.pipeline/<task-id>/**`，判据成立。

- 旧（错误）：`head` = `b4ca1179f30b054493e0c5227bcb86f3f6602e6b`（实现提交，早于修订提交 → 永远判过期）
- 新（本轮）：`head` = `observed_at_commit` = `875f4a5452b88932078b4a0f36db401604c39af1`（产生时的分支尖端）

## `gate pre-merge` 完整输出

命令（cwd = worktree 根）：

```
python -m pipeline_tools gate pre-merge .pipeline/derived-creation-removal --task-id derived-creation-removal --branch derived-creation-removal
```

### 修正前（run #1：磁盘上仍是 round 3 的报告，`head=b4ca117`；HEAD 已是 `875f4a5`）

```
FAIL: executor-report.md head does not match current Git identity; review-report.md head does not match current Git identity; final-check.md head does not match current Git identity
UNVERIFIED: goal hash unrecorded: docs/goal.md
exit=3
```

### 修正后（run #2：本报告以 `head=875f4a5` 写入工作树后；HEAD 仍是 `875f4a5`）

```
FAIL: review-report.md head does not match current Git identity; final-check.md head does not match current Git identity
UNVERIFIED: goal hash unrecorded: docs/goal.md
exit=3
```

**executor 的 `head does not match current Git identity` 已消失**（对比 run #1 的三条 → run #2 的两条）。余下两条属于**其它角色**的报告：`review-report.md`（reviewer round 1）与 `final-check.md`（main-final round 1）仍记录 `head=b4ca117`，同样早于 revision 3 的修订提交，因此仍被判过期。它们不是本轮可改的文件（本轮只重出 executor 证据），需由对应角色在**当前尖端**重出，或由主代理按项目规则裁定。

证据提交后 `head` 与当时的 `HEAD` 之间只差一个仅动 `.pipeline/derived-creation-removal/**` 的提交，走的是 `head_advanced_by_evidence_only` 的「仅证据推进」分支，结论不变（提交后复跑的完整输出见本轮交接说明）。

## 验收测试（逐条，命令见契约 `acceptance_tests[].command_ref`，cwd = worktree 根）

| ID | 命令 | 退出码 | 观察 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type` | 0 | 1 passed, 53 deselected |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived` | 0 | 1 passed, 53 deselected |
| acceptance-test-3 | `python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate` | 0 | 1 passed, 2 subtests passed |
| acceptance-test-4 | `python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed` | 0 | 1 passed, 63 deselected |
| acceptance-test-5 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 1 passed, 27 deselected |

## 全量测试

`python -m pytest -q`（cwd = worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）→ 退出码 0，**388 passed, 30 subtests passed**（与 round 2/3 一致，实现未变）。

## 其它检查（cwd = worktree 根）

- `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` → 退出码 0（PASS）。
- `python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor` → 退出码 0（PASS）。
- `python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed <revision 3 allowed_paths> --forbidden <revision 3 forbidden_paths>` → 退出码 0（PASS）。
- `git diff --check` → 退出码 0。
- `sha256sum docs/tasks/derived-creation-removal.md` = `ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd`（与 revision 3 记录一致）。
- 未改任何产品/测试/文档文件、未回退任何提交、未动主工作树与其它任务证据目录；本回合唯一写入是本证据目录下的两个文件。

```pipeline-evidence
{"schema": 2, "task_id": "derived-creation-removal", "worktree": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "branch": "derived-creation-removal", "role": "executor", "round": 4, "status": "PASS", "head": "875f4a5452b88932078b4a0f36db401604c39af1", "sheet_revision": 3, "sheet_sha256": "ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd", "observed_at_commit": "875f4a5452b88932078b4a0f36db401604c39af1", "generated_at": "2026-10-09T04:37:11+00:00", "commands": [{"command": "git rev-parse HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git rev-parse --show-toplevel", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "sha256sum docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools gate pre-merge .pipeline/derived-creation-removal --task-id derived-creation-removal --branch derived-creation-removal  # run 1, before rewriting this report, so executor-report.md still recorded head b4ca117", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 3, "expected_exit_code": 3, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed pipeline_tools/core.py pipeline_tools/planning.py pipeline_tools/__main__.py tests/test_planning.py tests/test_task_generation.py tests/test_derived_task_dispatch_recovery.py tests/test_security_repairs.py tests/test_cli.py tests/test_acceptance_id_and_template_compliance.py SKILL.md README.md references/task-design.md references/compat-and-migration.md docs/tasks/derived-creation-removal.md .pipeline/derived-creation-removal/** --forbidden docs/goal.md pipeline_tools/contract.py .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/finalization-report-reader/** .pipeline/finalization-hygiene/** .env credentials/**", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}], "assertions": ["head and observed_at_commit now record the branch tip at the time the evidence was produced (875f4a5), not the implementation commit (b4ca117), so the range to any later evidence commit contains only .pipeline paths", "run 1 of gate pre-merge, taken with the round 3 report on disk, still showed three head mismatches; run 2, taken with this report on disk, no longer reports the executor-report head mismatch", "no implementation, test or documentation file changed: git status stayed clean apart from this evidence directory and the implementation diff against b4ca117 is empty", "all five acceptance commands exit 0 and the full suite is green at 388 passed, 30 subtests passed", "the task sheet hash still matches the revision 3 record in the amendment chain at ff027c6d"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["round 4 corrects the head semantics: head and observed_at_commit now name the branch tip at the moment the evidence was produced (875f4a5) instead of the implementation commit b4ca117, which predated the contract amendments and could never satisfy the evidence-only advance rule", "review-report.md and final-check.md still record head b4ca117; they are other roles' evidence for earlier rounds and are not rewritten here, so the gate still reports their head mismatch until those roles re-produce them", "the gate reports UNVERIFIED goal hash unrecorded: docs/goal.md, unchanged from earlier rounds; this task neither modified docs/goal.md nor recorded a hash for it", "the pre-commit gate run predates this evidence commit, so its head comparison used 875f4a5 as the current HEAD; the post-commit run is recorded in the round handoff", "no new runtime behaviour was observed beyond re-running the same commands, because the implementation and tests are byte-identical to the previous rounds"]}
```
