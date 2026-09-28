# 执行者报告：test-ref-narrowing-followup

## 任务身份

- task-id：`test-ref-narrowing-followup`
- 类型：`prerequisite`（规划期机械底座，无用户可观察完成）
- worktree：`D:\Projects\Skills\pipeline\.worktrees\test-ref-narrowing-followup`
- branch：`test-ref-narrowing-followup`
- baseline：`f0e5b7c`（Freeze generated task test-ref-narrowing-followup）
- 执行提交：`5a41b87b1749e08f0a2e3911786192518503314b`
- 轮次：1

## 1. 读了哪些文件

任务单、`goal.md`、`references/execution-and-review.md`、`references/acceptance-evidence.md`、`references/task-design.md`、`templates/pipeline-evidence.json`；`pipeline_tools/planning.py`（全文，重点 `_covers_path`/`_shares_test_root`/`_validate_test_ref_placement`/调用点）；三个 fixture 文件全文；`tests/test_planning.py:693/724`；`tests/test_acceptance_id_and_template_compliance.py:274-285`。

## 2. 删掉的两行（改前改后对照）

`pipeline_tools/planning.py` 的 `_validate_test_ref_placement`。

**改前**（`claimed` 列表 + 空集静默放行，即收窄豁免）：

```python
        path = _test_ref_path(record.get("test_ref"))
        if path is None:
            continue
        claimed = [
            item for item in allowed_paths
            if _covers_path(item, path) or _shares_test_root(item, path)
        ]
        if not claimed:
            continue
        if any(_covers_path(item, path) for item in allowed_paths):
            continue
```

**改后**（无条件判定）：

```python
        path = _test_ref_path(record.get("test_ref"))
        if path is None:
            continue
        if any(_covers_path(item, path) for item in allowed_paths):
            continue
```

删掉的是 `claimed = [...]`（3 行）与 `if not claimed: continue`（2 行，其中 `claimed` 判定含 `_shares_test_root`）。**`_shares_test_root` 函数本身保留未动**（`planning.py:669`），`:705` 之后 `claimed` 非空时的覆盖判定逻辑等价并入无条件判定。docstring 同步改写为「检查是无条件的」。

## 3. 中间态（迁移前）全量结果

```
Ran 285 tests in 156.530s
FAILED (failures=22)
```

22 条全部是 `test_ref ... is outside the task's allowed paths`，分布：`test_planning_dispatch_integration.py` 15、`test_task_plan_contract_consistency.py` 3、`test_cli.py` 4。

## 4. 22 条 fixture 完整清单

| # | 文件:行号 | 测试名 | 原 resources | test_ref | 迁移后 resources |
|---|---|---|---|---|---|
| 1 | test_planning_dispatch_integration.py:54 | test_successful_dispatch_persists_no_planning_artifacts | `resource`(src/app.py) | tests/test_planning_dispatch_integration.py | + `tests/test_planning_dispatch_integration.py` |
| 2 | 同上:54 | test_project_approval_mode_is_the_default_and_run_state_wins | 同上 | 同上 | 同上 |
| 3 | 同上:54 | test_run_state_approval_mode_takes_precedence_over_project_config | 同上 | 同上 | 同上 |
| 4 | 同上:54 | test_explicit_argument_approval_mode_overrides_project_config | 同上 | 同上 | 同上 |
| 5 | 同上:54 | test_planning_to_dispatch_preserves_complete_facts_envelope_and_blocks_conflicts_end_to_end | 同上 | 同上 | 同上 |
| 6 | 同上:54 | test_decision_blocker_states_gate_dispatch_end_to_end (×2 subtests) | 同上 | 同上 | 同上 |
| 7 | 同上:54 | test_valid_planning_run_reaches_identity_verified_dispatch | 同上 | 同上 | 同上 |
| 8 | 同上:54 | test_automatic_approval_dispatches_without_explicit_approve | 同上 | 同上 | 同上 |
| 9 | 同上:54 | test_manual_approval_requires_explicit_approve_before_dispatch | 同上 | 同上 | 同上 |
| 10 | 同上:54 | test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts (×3 subtests) | 同上 | 同上 | 同上 |
| 11 | 同上:54 | test_dispatch_failure_does_not_create_or_replace_worktree | 同上 | 同上 | 同上 |
| 12 | 同上:54 | test_successful_dispatch_after_run_start_leaves_no_lifecycle | 同上 | 同上 | 同上 |
| 13 | test_task_plan_contract_consistency.py:16 | test_matching_plan_and_schema2_sheet_pass | pipeline_tools/planning.py | tests/test_x.py | + `tests/test_x.py`（plan + contract allowed_paths/resources） |
| 14 | 同上:16 | test_schema3_non_goals_and_allowed_paths_are_compared | 同上 | 同上 | 同上 |
| 15 | 同上:73 | test_shared_acceptance_test_across_operations_passes_contract_consistency | 同上 | 同上 | 同上 |
| 16 | test_cli.py:108 | test_planning_generate_task_sheets_cli_lifecycle | resource(src/app.py) | tests/test_cli.py | + `{'id':'test-resource','path':'tests/test_cli.py'}` |
| 17 | test_cli.py:228 | test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet | pipeline_tools/planning.py | tests/test_cli.py | + `tests/test_cli.py`（plan + contract allowed_paths/resources） |
| 18 | test_cli.py:479 | test_planning_to_dispatch_cli_blocks_when_facts_envelope_has_conflicts | ok.txt | tests/test_cli.py | + test-resource（未直接变红，随 _dispatch_inputs 形态统一） |
| 19 | test_cli.py:766 | test_planning_to_dispatch_cli_contract_and_failure_boundaries | src/app.py | tests/test_cli.py | + test-resource，后修正 plan.resources 为字面 `tests/test_cli.py` |
| 20 | test_cli.py:817 | test_planning_to_dispatch_cli_resolves_recorded_then_project_then_explicit | ok.txt | tests/test_cli.py | 同 #19（经 `_dispatch_inputs`） |
| 21 | test_cli.py:803 | test_task_plan_contract_consistency_cli（sheet 内 acceptance） | pipeline_tools/planning.py | tests/test_cli.py | + `tests/test_cli.py`（contract allowed_paths/resources） |
| 22 | test_planning_dispatch_integration.py:31 | （inputs() 共同 fixture，覆盖 #1–#12） | resource | tests/test_planning_dispatch_integration.py | + `tests/test_planning_dispatch_integration.py` |

> 说明：#1–#12 与 #22 共用 `inputs()`；#13–#15 共用两个 fixture builder；#18、#20 共用 `_dispatch_inputs`。表中行号为迁移前基线位置。

## 5. 迁移中的期望值机械派生变化（逐处对照）

**无任何断言被削弱或删除。** 改动只落在 fixture 的**输入数据**（`resources` / plan 的 `resources` / contract 的 `resources` 与 `allowed_paths`）。逐处机械派生：

- `tests/test_task_plan_contract_consistency.py:17/76/109`：contract 的 `allowed_paths` 由 `["pipeline_tools/planning.py"]` → `["pipeline_tools/planning.py","tests/test_x.py"]`。这是 `resources` 的机械派生（`_task_allowed_paths` 直接取 resources），非放宽断言。
- `tests/test_task_plan_contract_consistency.py:134`：`value["allowed_paths"] = ["src/**"]`（drift 用例）保持原样，仍断言 `status == "fail"` 且 field 为 `allowed_paths` —— 断言未动。
- `tests/test_cli.py:807`：contract 的 `allowed_paths`/`resources` 同步加 `tests/test_cli.py`，属同一机械派生。
- 其余 fixture 只改 `resources` 数组，未触碰任何 `assertXxx`。

**断言文本本身被修改的地方**：仅 `tests/test_acceptance_id_and_template_compliance.py:282-285` 新增 5 条断言（见第 7 节），属任务要求的「收紧」，不是放宽。

## 6. 文档整节改写前后对照

`references/task-design.md` 的 `### \`test_ref\` 的位置规则`。

**收窄表述 1（bullet 限定语）**

- 改前：`- 规划期（\`pipeline_tools/planning.py\`）：当任务声明的资源与 \`test_ref\` 位于同一目录树时，\`test_ref\` 指名的文件必须落在任务的 \`allowed_paths\` 之内。…`
- 改后：`- 规划期（\`pipeline_tools/planning.py\`）：\`test_ref\` 指名的文件必须落在任务的 \`allowed_paths\` 之内；这条判定是无条件的，不因任务是否声明了与测试同目录树的资源而改变。…`（限定语删除，改无条件）

**收窄表述 2（豁免句）**

- 改前：`任务若未声明与 \`test_ref\` 同目录树的资源，视为不对该目录提出归属主张，规划期位置校验不生效；这类验收记录仍受其余结构校验约束。`
- 改后：**整句删除**，该段移除。

## 7. 文档测试收紧的断言对照

`tests/test_acceptance_id_and_template_compliance.py:274-285`。

- 改前（保留）：`test_ref`/`allowed_paths`/`planning.py`/`core.py` 子串；`` `test_ref` 的位置规则 ``；`类名.方法名`；`is outside the task's allowed paths`；`absent`。
- 改后**新增**：
  - `self.assertIn("`test_ref` 指名的文件必须落在任务的 `allowed_paths` 之内", task_design)`（肯定：无条件表述）
  - `self.assertIn("无条件", task_design)`
  - `self.assertNotIn("不主张归属", task_design)`
  - `self.assertNotIn("提出归属主张", task_design)`
  - `self.assertNotIn("位置校验不生效", task_design)`（否定：不得含豁免措辞）

原有合理断言全部保留。断言据改写后的文档正文实测通过（A8 exit 0）。

## 8. 另外 2 条测试的确认（op-cover-strict-test-ref-placement）

- `PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources`（:693）：plan.resources=`tests/test_planning.py`，test_ref=`tests/test_evidence.py`，断言 `any('outside' in error)`。严格规则下仍成立，**无需调整**，实测 PASS。
- `PlanningTests.test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned`（:724）：plan.resources=`tests/test_evidence.py`，test_ref=`tests/test_acceptance_id_and_template_compliance.py`（同目录树但不拥有）。收窄下靠 `_shares_test_root` 命中；严格下由无条件判定直接命中。语义仍成立，**无需调整**，实测 PASS。

## 9. 测试结果（准确数字）

| 阶段 | 命令 | 结果 | 耗时 |
|---|---|---|---|
| 基线（未改代码） | `unittest discover -s tests` | Ran 285 tests, **OK** | 189.995s |
| 删收窄后（迁移前） | 同上 | Ran 285 tests, **FAILED (failures=22)** | 156.530s |
| 最终（迁移后） | 同上 | Ran 285 tests, **OK** | 211.295s |

## 10. 8 条 acceptance 逐条结果

| id | 命令 | exit | 结果 |
|---|---|---|---|
| acceptance-test-planner-rejects-out-of-scope-test-ref | `unittest tests.test_planning.PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources` | 0 | OK |
| acceptance-test-planner-rejects-unowned-test-ref-in-shared-root | `...test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned` | 0 | OK |
| acceptance-test-cli-generate-task-sheets-lifecycle-passes | `...test_planning_generate_task_sheets_cli_lifecycle` | 0 | OK |
| acceptance-test-cli-contract-consistency-schema2-passes | `...test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet` | 0 | OK |
| acceptance-test-dispatch-valid-run-reaches-identity-verified-dispatch | `...test_valid_planning_run_reaches_identity_verified_dispatch` | 0 | OK |
| acceptance-test-dispatch-conflict-fails-closed | `...test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts` | 0 | OK |
| acceptance-test-contract-consistency-matching-plan-and-schema2-pass | `...test_matching_plan_and_schema2_sheet_pass` | 0 | OK |
| acceptance-test-strict-test-ref-placement-documented | `...test_references_task_design_documents_test_ref_placement_and_position_rules` | 0 | OK |

红→绿转换：A3/A4/A5/A6/A7 在迁移前为 FAIL（见第 3 节中间态），迁移后全部 OK。

## 11. 端到端验证（第八步三项）

1. `task validate docs/tasks/test-ref-narrowing-followup.md` → `{"status":"pass","errors":[]}` exit 0。**新规则不误伤本任务自己**（8 条 test_ref 均在自身 allowed_paths 内）。
2. `gate pre-merge .pipeline/test-ref-narrowing-followup --task-id test-ref-narrowing-followup` → `{"status":"blocked","errors":["missing executor-report.md","missing review-report.md","missing final-check.md","missing executor-result.json","missing reviewer-result.json","missing final-result.json"]}` exit 3。此刻只有 executor 一份，**预期 blocked 且提及缺 review/final**，符合预期。
3. `freshness . .pipeline/test-ref-narrowing-followup --result .pipeline/test-ref-narrowing-followup/executor-result.json` → 见第 13 节自检；`errors: []`、`evidence_only: true`、`status: pass`。

## 12. 提交

- `5a41b87 fix(planning): remove test_ref narrowing exemption and migrate fixtures`（37 字符 ≤72，无署名/emoji）
- `git show --stat HEAD`：`planning.py` 14 行、`references/task-design.md` 4 行、`tests/test_acceptance_id_and_template_compliance.py` 7 行、`tests/test_cli.py` 16 行、`tests/test_planning_dispatch_integration.py` 4 行、`tests/test_task_plan_contract_consistency.py` 18 行；6 files changed, 30 insertions(+), 33 deletions(-)。

## 13. 自检

- `git status --short`：仅 `?? .pipeline/metrics/*.json`（仓库常态，未跟踪）。
- 证据目录 `git ls-files .pipeline/test-ref-narrowing-followup/`：仅 `executor-report.md`、`executor-result.json`。
- **未提交任何 `.log` 文件进证据目录。**

## 14. 任务单字节未变

- 现在：`sha256sum docs/tasks/test-ref-narrowing-followup.md` = `c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93`
- baseline：`git show f0e5b7c:docs/tasks/test-ref-narrowing-followup.md | sha256sum` = `c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93`
- **完全一致，冻结任务单未改。**

## 15. 异常与需裁决项

- **无失败或未完成项。** 交付完整：4 个 operation 全部落地，全量 285 OK。
- 迁移中一度出现 2 条残留 FAIL（`_dispatch_inputs` 与 CLI 边界用例的 plan.resources 用了别名 `test-resource`，而 `compare_task_plan_contract` 不传 project_facts 无法解析别名）。已修正为字面路径 `tests/test_cli.py`，属迁移形态修正，未放宽断言。

## 16. 无法确定项

- `unknown-historic-41-count`（任务单已记 non_blocking）：终审记录 41/22 vs 37/18 的差异本任务无法独立复现；本轮进程内实测中间态为 22 条，与 22 一致。

## 17. 裁决后补记：执行者证据状态大小写对齐（C4）

**事实**：`executor-result.json` 顶层 `status` 用 `READY-TO-MERGE`、8 条 `acceptance[].status` 用 `PASS`（大写）；而 `result verify` 侧的 `verify_structured_result`（`pipeline_tools/core.py:1201`）只接受小写 `{pass, fail, blocked, flaky}`，`:1213` 的 acceptance 只接受小写 `{pass, fail, blocked, flaky, unverified}`。gate 侧 `evidence_verify`（`pipeline_tools/core.py:364`）读 markdown 的 ` ```pipeline-evidence ` 块时 `valid_statuses` 却是大写集合（`PASS`/`FAIL`/`BLOCKED`/`FLAKY`/`EXPLORATORY_ONLY`/`READY-TO-MERGE`/`MERGED`），`gate_check`（`:1670`）进一步要求 `PASS`/`READY-TO-MERGE`。两套约定方向相反且并存。

**缺陷性质**：执行者只满足了 gate 侧（markdown 证据块大写），未满足 `result verify` 侧（JSON 机器结果需小写），而原报告第 15 节称「无失败或未完成项」，未涵盖此点。

**授权来源**：主代理（用户明确裁决「修 executor-result.json」）。

**改了什么**（逐字段，只改大小写，不改语义、不改 ID、不改 `identity`、不改 `acceptance` 条目集合）：

| 文件 | 字段 | 改前 | 改后 |
|---|---|---|---|
| `.pipeline/test-ref-narrowing-followup/executor-result.json` | 顶层 `status` | `READY-TO-MERGE` | `pass` |
| 同上 | 8 条 `acceptance[].status` | `PASS` | `pass` |

**未改**：`executor-report.md` 的 ` ```pipeline-evidence ` 块（那一侧要大写，本来就是对的）；`identity`；`acceptance` 条目集合；`commands` / `assertions` / `unverified` / `evidence_refs`。

**遗留**：`result verify`（要求小写）与 gate 证据块（要求大写）两套约定方向相反，属工具链既有张力，不在本任务范围。

**证据时序瑕疵补记**：原报告第 11.2 节记录的 `gate pre-merge` 输出为 6 项缺失（含 `executor-report.md`、`executor-result.json`），与复核时实测的 4 项缺失不一致。审查者已核实：该 gate 命令在 executor 证据落盘之前执行，输出在当时真实，属证据时序问题而非记录错误。

```pipeline-evidence
{"schema":1,"task_id":"test-ref-narrowing-followup","worktree":".worktrees/test-ref-narrowing-followup","branch":"test-ref-narrowing-followup","role":"executor","round":1,"status":"PASS","commands":[{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests (after removing narrowing, before migration)","exit_code":1,"expected_exit_code":1,"evidence_ref":"executor-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests (final)","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_cli.CLITests.test_planning_generate_task_sheets_cli_lifecycle","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_cli.CLITests.test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pipeline_tools --format json task validate docs/tasks/test-ref-narrowing-followup.md","exit_code":0,"evidence_ref":"executor-report.md"},{"command":"python -m pipeline_tools --format json gate pre-merge .pipeline/test-ref-narrowing-followup --task-id test-ref-narrowing-followup","exit_code":3,"expected_exit_code":3,"evidence_ref":"executor-report.md"},{"command":"python -m pipeline_tools --format json freshness . .pipeline/test-ref-narrowing-followup --result .pipeline/test-ref-narrowing-followup/executor-result.json","exit_code":0,"evidence_ref":"executor-report.md"}],"assertions":["pipeline_tools/planning.py _validate_test_ref_placement: removed 'claimed = [...]' and 'if not claimed: continue'; now unconditional 'if any(_covers_path(item, path) for item in allowed_paths): continue'.","Intermediate state after code change: Ran 285 tests, FAILED (failures=22), all 'test_ref ... is outside the task's allowed paths'.","Final state after fixture migration: Ran 285 tests, OK, 211.295s, 0 failures.","All 8 acceptance tests pass with exit_code 0.","No assertion was weakened, deleted or skipped; only fixture resources input data changed.","references/task-design.md no longer contains '不主张归属', '提出归属主张' or '位置校验不生效'.","tests/test_acceptance_id_and_template_compliance.py adds positive unconditional assertion and negative exemption assertions.","Frozen task sheet sha256 unchanged vs baseline f0e5b7c."],"evidence_refs":["executor-report.md","executor-result.json"],"unverified":["independent review","final check","merge to main"]}
```