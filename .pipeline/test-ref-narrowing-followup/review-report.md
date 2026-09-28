# 审查者报告：test-ref-narrowing-followup

## 任务身份

- task-id：`test-ref-narrowing-followup`
- 类型：`prerequisite`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\test-ref-narrowing-followup`
- branch：`test-ref-narrowing-followup`
- baseline：`f0e5b7c`
- 被审提交链：`5a41b87`（实现）→ `04dc81b`（证据），审查时 HEAD `04dc81b`
- 轮次：1
- 角色：reviewer（独立验证，不采信执行者自述）

## 结论摘要

**ACCEPT WITH CONDITIONS。** 核心改动（删除收窄豁免、无条件判定、22 条 fixture 迁移、文档整节改写、文档测试收紧）经独立复现全部成立；全量 285 OK；8 条 acceptance 全部 exit 0。执行者自述的「中间态 22 条失败」被独立复现为**22 条真实收窄失败 + 1 条环境伪影**。发现两处非阻塞瑕疵（见下）。

---

## A. 提交与边界

### A.1 提交链

```
04dc81b chore(test-ref-narrowing-followup): add executor evidence
5a41b87 fix(planning): remove test_ref narrowing exemption and migrate fixtures
f0e5b7c Freeze generated task test-ref-narrowing-followup
```

`git worktree list --porcelain` 确认本 worktree 路径/分支/task-id 与 dispatch 一致；主工作树 `D:/Projects/Skills/pipeline` 在 `main`。

`git show --stat 5a41b87`：6 files changed, 30 insertions(+), 33 deletions(-) —— `pipeline_tools/planning.py` 14、`references/task-design.md` 4、`tests/test_acceptance_id_and_template_compliance.py` 7、`tests/test_cli.py` 16、`tests/test_planning_dispatch_integration.py` 4、`tests/test_task_plan_contract_consistency.py` 18。

`git show --stat 04dc81b`：仅新增 `executor-report.md`、`executor-result.json` 两个证据文件。

### A.2 `git diff f0e5b7c HEAD --name-status`

```
A  .pipeline/test-ref-narrowing-followup/executor-report.md
A  .pipeline/test-ref-narrowing-followup/executor-result.json
M  pipeline_tools/planning.py
M  references/task-design.md
M  tests/test_acceptance_id_and_template_compliance.py
M  tests/test_cli.py
M  tests/test_planning_dispatch_integration.py
M  tests/test_task_plan_contract_consistency.py
```

### A.3 `allowed_paths` 边界（7 项）

非证据改动共 6 个文件，**逐条**落在 7 项 allowed_paths 内：`pipeline_tools/planning.py`、`tests/test_planning.py`（本轮未改）、`tests/test_acceptance_id_and_template_compliance.py`、`references/task-design.md`、`tests/test_cli.py`、`tests/test_planning_dispatch_integration.py`、`tests/test_task_plan_contract_consistency.py`。**无越界文件。** 两个证据文件在 `.pipeline/test-ref-narrowing-followup/` 内，属允许。

### A.4 metrics 删除

`git diff f0e5b7c HEAD --name-status -- .pipeline/metrics/` 输出为空。**未删除任何 metrics 文件（=0）。** `git status --short` 仅 9 个未跟踪 `.pipeline/metrics/*.json`（仓库常态）；`--untracked-files=no` 干净。

## B. 任务单字节未变

```
sha256sum docs/tasks/.../test-ref-narrowing-followup.md
  = c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93
git show f0e5b7c:docs/tasks/.../test-ref-narrowing-followup.md | sha256sum
  = c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93
```

一致，与执行者报告相同。**冻结任务单未改。**

## C. 核心代码改动（最重要）

### C.1 改后 `_validate_test_ref_placement` 全文

```python
def _validate_test_ref_placement(
    declared: set[str],
    records: dict[str, dict[str, Any]],
    allowed_paths: list[str],
    errors: list[str],
    *,
    task_id: str,
) -> None:
    """Reject an acceptance test_ref that points outside the task's resources.

    The check is unconditional: the file named by ``test_ref`` must fall inside
    the task's ``allowed_paths``, whether or not the task declares a resource in
    the same directory tree.
    """
    for test_id in sorted(declared):
        record = records.get(test_id)
        if not isinstance(record, dict):
            continue
        path = _test_ref_path(record.get("test_ref"))
        if path is None:
            continue
        if any(_covers_path(item, path) for item in allowed_paths):
            continue
        errors.append(
            f"task {task_id} acceptance test {test_id} test_ref {path} is outside "
            "the task's allowed paths"
        )
```

### C.2 收窄豁免确已删除

- 基线 `git show f0e5b7c:pipeline_tools/planning.py | grep -n "if not claimed"` → `703:        if not claimed:`（**存在**）
- HEAD `grep -n "if not claimed" pipeline_tools/planning.py` → 无命中（exit 1）；`grep -n "claimed"` → 无命中（exit 1）

diff 中删除的原始 6 行为：

```python
        claimed = [
            item for item in allowed_paths
            if _covers_path(item, path) or _shares_test_root(item, path)
        ]
        if not claimed:
            continue
```

### C.3 判定变为无条件

HEAD 判定链为 `path is None → continue` 后**直接** `if any(_covers_path(item, path) for item in allowed_paths): continue`。空集不再静默放行。**成立。**

### C.4 `_shares_test_root` 未动

`grep -n "_shares_test_root" pipeline_tools/planning.py` → 仅 `669:def _shares_test_root(...)`（定义仍在，成为死代码）。`git diff f0e5b7c HEAD -- pipeline_tools/planning.py` 全文只有两处 hunk：docstring 改写 + 上述 6 行删除。**该函数确未被改动，与执行者自述一致。**

### C.5 无额外放宽

`_covers_path` 全文（HEAD）未被 diff 触及，仍只有三条分支：`allowed.endswith("/")` 前缀、`allowed.endswith("/*")` 前缀、否则 `candidate == allowed or candidate.startswith(allowed + "/")`。**没有新增宽泛分支。**

### C.6 调用点未变

`grep -n "_validate_test_ref_placement" pipeline_tools/planning.py` → 定义 `:676`、调用 `:1157`。调用点仍包在 `if task_allowed_paths:` 内，参数形态不变（`declared, accepted_records, task_allowed_paths, errors, task_id=identifier`）。**未改。**

## D. 22 条 fixture 迁移对照

`git diff f0e5b7c HEAD -- tests/test_cli.py tests/test_planning_dispatch_integration.py tests/test_task_plan_contract_consistency.py` 全文读取；对 `tests/` 全部改动做断言行扫描：

```
git diff ... -- tests/ | grep -E "^[+-].*(skip|expectedFailure|assertIn|assertEqual|assertNotIn|assertTrue|assertFalse)"
```

命中**仅** `test_acceptance_id_and_template_compliance.py` 新增的 5 行（`assertIn`×2 + `assertNotIn`×3）。对三个 fixture 文件单独扫描：

```
git diff ... -- <three fixture files> | grep -E "^[+-].*(assert|skip|expectedFailure)"
→ NONE: zero assertion/skip lines touched in the three fixture files
```

**逐处对照结论：**

- `tests/test_planning_dispatch_integration.py`：唯一改动是 `inputs()` 中 plan 的 `resources` 与 task 的 `resources` 各加 `"tests/test_planning_dispatch_integration.py"`。**零断言改动。**
- `tests/test_task_plan_contract_consistency.py`：三处 builder 的 plan/contract `resources` 与 `allowed_paths` 各加 `"tests/test_x.py"`（机械派生）。`test_schema3_...` 里原有的 drift 用例 `allowed_paths=["src/**"]` 与 `status=="fail"` 断言**未动**。**零断言改动。**
- `tests/test_cli.py`：四处 fixture 的 `resources` / contract `allowed_paths` 加 `tests/test_cli.py`。**零断言改动。**

**没有**删除断言、加 `skip`、加 `expectedFailure`、放宽边界值，或把 `assertEqual` 改成 `assertIn`。执行者自述「唯一断言文本被改的地方是文档合规测试新增 5 条收紧断言」与「其余为机械派生」**两点均成立**。

`git diff f0e5b7c HEAD --stat -- tests/test_planning.py` 为空：**`test_planning.py` 未被改动**（符合契约：该文件的验收测试在基线即已存在且语义已正确）。

## E. 红绿转换的独立复现（核心证伪）

### E.1 最终态（HEAD 全量）

worktree 内 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests`：

```
Ran 285 tests in 186.050s
OK
```

**285 测试全绿，0 失败**，与执行者报告的最终态一致（耗时 186s vs 执行者 211s，属环境差异）。

### E.2 中间态（temp 树）

`git archive f0e5b7c` 解到系统 temp，**只**把 `pipeline_tools/planning.py` 换成 HEAD 版本（验证 `grep "if not claimed"` 无命中），跑全量：

```
Ran 285 tests in 163.784s
FAILED (failures=23)
```

**实测 23 条失败，非执行者所称的 22 条。** 但逐条核查后，其中 **22 条是收窄规则引发**，**1 条是 temp 树环境伪影**：

- 伪影：`test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_tracked_pipeline_evidence_contains_only_retained_names`，`AssertionError: 128 != 0 : fatal: not a git repository`。该测试在 `ROOT` 下执行 `git ls-files .pipeline`；`git archive` 出来的 temp 树**没有 `.git`**，故必然失败。**证伪**：在**未改任何代码**的 pristine `f0e5b7c` temp 树上单跑该测试，同样 `FAILED (failures=1)`，`128 != 0 : fatal: not a git repository`。**故该条与收窄规则无关，是 temp 树无法复现的仓库依赖测试。**

### E.3 收窄引发的 22 条完整清单（实测）

`test_planning_dispatch_integration.py`（15）：
1. `test_automatic_approval_dispatches_without_explicit_approve`
2. `test_decision_blocker_states_gate_dispatch_end_to_end` (status='resolved')
3. `test_decision_blocker_states_gate_dispatch_end_to_end` (status='non_blocking')
4. `test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts` (variant='same')
5. `test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts` (variant='different')
6. `test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts` (variant='hash-drift')
7. `test_dispatch_failure_does_not_create_or_replace_worktree`
8. `test_explicit_argument_approval_mode_overrides_project_config`
9. `test_manual_approval_requires_explicit_approve_before_dispatch`
10. `test_planning_to_dispatch_preserves_complete_facts_envelope_and_blocks_conflicts_end_to_end`
11. `test_project_approval_mode_is_the_default_and_run_state_wins`
12. `test_run_state_approval_mode_takes_precedence_over_project_config`
13. `test_successful_dispatch_after_run_start_leaves_no_lifecycle`
14. `test_successful_dispatch_persists_no_planning_artifacts`
15. `test_valid_planning_run_reaches_identity_verified_dispatch`

`test_cli.py`（4）：
16. `test_planning_generate_task_sheets_cli_lifecycle`
17. `test_planning_to_dispatch_cli_contract_and_failure_boundaries`
18. `test_planning_to_dispatch_cli_resolves_recorded_then_project_then_explicit`
19. `test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet`

`test_task_plan_contract_consistency.py`（3）：
20. `test_matching_plan_and_schema2_sheet_pass`
21. `test_schema3_non_goals_and_allowed_paths_are_compared`
22. `test_shared_acceptance_test_across_operations_passes_contract_consistency`

**分布 = 15 + 4 + 3 = 22**，与执行者报告的分布**完全一致**。除伪影外，**22 条全部落在三个 fixture 文件内，无一落在别处**。所有失败根因均为 `test_ref ... is outside the task's allowed paths`（断言文本 `'blocked' != 'dispatch-ready'`、`'fail' != 'pass'`、`3 != 0` 均为该上游错误的派生表现）。

### E.4 与执行者清单对照（M 步）

执行者报告 §4 的 22 条清单：`test_planning_dispatch_integration.py` 15 + `test_task_plan_contract_consistency.py` 3 + `test_cli.py` 4。与 E.3 实测集**逐条一致**（含 `test_decision_blocker_states_gate_dispatch_end_to_end` 的 2 个 subtest、`test_dispatch_conflict_...` 的 3 个 subtest）。执行者的**计数与分布准确**，仅其「Ran 285 / failures=22」少算了 temp 树特有的 1 条 git 仓库伪影（其在真实 worktree 内跑，无此伪影，故其 22 反而是正确口径）。

## F. 文档整节改写

### F.1 改后全文（该标题到 `### 证据等级下限表` 之前）

```
### `test_ref` 的位置规则

`test_ref` 的书写格式是 `文件路径: 类名.方法名`，冒号前的文件路径是项目相对路径，冒号后的符号目标是可选位置声明；`test_ref` 与 `command_ref` 都不含尖括号。

位置规则分两层，分别由规划期和 gate 期机械校验：

- 规划期（`pipeline_tools/planning.py`）：`test_ref` 指名的文件必须落在任务的 `allowed_paths` 之内；这条判定是无条件的，不因任务是否声明了与测试同目录树的资源而改变。允许的写法包括精确路径、目录前缀（`tests/` 结尾）和通配（`tests/*`）。落在任务资源范围之外的验收测试会被判 `... test_ref ... is outside the task's allowed paths`。
- gate 期（`pipeline_tools/core.py`）：`test_ref` 指名的文件必须真实存在，且当 `test_ref` 声明了类名或方法名时，该符号必须在文件里真实声明；缺失会被判 `... test_ref method is absent from ...`。gate 只做位置与存在性核验，不解释测试语义。
```

### F.2 两处收窄表述都处理了

- **限定语**：原「当任务声明的资源与 `test_ref` 位于同一��录树时」**已删除**，改为「这条判定是无条件的，不因任务是否声明了与测试同目录树的资源而改变」。
- **豁免句**：「任务若未声明与 `test_ref` 同目录树的资源，视为不对该目录提出归属主张，规划期位置校验不生效；这类验收记录仍受其余结构校验约束。」**整句删除**（diff 显示该段连同其后空行被删）。

### F.3 残余收窄措辞

`grep -n "不主张归属\|提出归属主张\|位置校验不生效\|同目录树" references/task-design.md` → **仅 1 处命中**（`:104`），且位于**否定收窄的新表述**内：「不因任务是否声明了与测试**同目录树**的资源而改变」。`不主张归属` / `提出归属主张` / `位置校验不生效` **零命中**。**无残余收窄措辞。**

### F.4 改写后与实现一致

文档描述无条件的「必须落在 `allowed_paths` 之内」，与 C.1–C.3 的实现一致。**成立。**

## G. 文档测试收紧

### G.1 改后方法体

```python
    def test_references_task_design_documents_test_ref_placement_and_position_rules(self):
        task_design = (ROOT / "references/task-design.md").read_text(encoding="utf-8")
        acceptance = (ROOT / "references/acceptance-evidence.md").read_text(encoding="utf-8")
        for text in (task_design, acceptance):
            self.assertIn("test_ref", text)
            self.assertIn("allowed_paths", text)
            self.assertIn("planning.py", text)
            self.assertIn("core.py", text)
        self.assertIn("`test_ref` 的位置规则", task_design)
        self.assertIn("类名.方法名", acceptance)
        self.assertIn("is outside the task's allowed paths", task_design)
        self.assertIn("absent", task_design)
        # 严格规则：规划期位置校验必须写成无条件约束。
        self.assertIn("`test_ref` 指名的文件必须落在任务的 `allowed_paths` 之内", task_design)
        self.assertIn("无条件", task_design)
        # 文档不得再保留任何收窄豁免措辞。
        self.assertNotIn("不主张归属", task_design)
        self.assertNotIn("提出归属主张", task_design)
        self.assertNotIn("位置校验不生效", task_design)
```

### G.2 两种断言都在

- **否定断言**：`assertNotIn("不主张归属"/"提出归属主张"/"位置校验不生效")` ✓
- **肯定断言**：`assertIn("`test_ref` 指名的文件必须落在任务的 `allowed_paths` 之内")` + `assertIn("无条件")` ✓

### G.3 原断言未被删

`test_ref`、`allowed_paths`、`planning.py`、`core.py`、`` `test_ref` 的位置规则 ``、`类名.方法名`、`is outside the task's allowed paths`、`absent` **全部保留**。

### G.4 实跑

```
python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules
Ran 1 test in 0.001s
OK
EXIT=0
```

### G.5 区分力（独立验证）

在 temp 副本（`git archive HEAD`）中把文档临时改回含豁免措辞（重新插入「不主张归属」「位置校验不生效」等），**只改 temp，不落仓库**：

- 真实文档：`OK`，`BASELINE_EXIT=0`
- 变异文档：`FAILED (failures=1)`，`AssertionError: '提出归属主张' unexpectedly found`，`MUTATED_EXIT=1`

**该测试有区分力，断言有效。**

## H. 另两条测试确认

- `test_task_plan_rejects_acceptance_test_ref_outside_task_resources`（`:693`）：plan.resources=`tests/test_planning.py`，test_ref=`tests/test_evidence.py`，断言 `any('outside' in error)`。严格规则下仍成立。实跑 `OK`，EXIT=0。
- `test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned`（`:724`）：plan.resources=`tests/test_evidence.py`，test_ref=`tests/test_acceptance_id_and_template_compliance.py`（同目录树但不拥有）。收窄下靠 `_shares_test_root` 命中豁免，严格下由无条件判定直接命中。语义仍成立。实跑 `OK`，EXIT=0。

两条在基线即已存在（`git show f0e5b7c:tests/test_planning.py` 确认），本轮未改动。

## I. 8 条 acceptance 逐条实跑

| id | 命令（截断） | exit |
|---|---|---|
| acceptance-test-planner-rejects-out-of-scope-test-ref | `...test_task_plan_rejects_acceptance_test_ref_outside_task_resources` | 0 |
| acceptance-test-planner-rejects-unowned-test-ref-in-shared-root | `...test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned` | 0 |
| acceptance-test-cli-generate-task-sheets-lifecycle-passes | `...test_planning_generate_task_sheets_cli_lifecycle` | 0 |
| acceptance-test-cli-contract-consistency-schema2-passes | `...test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet` | 0 |
| acceptance-test-dispatch-valid-run-reaches-identity-verified-dispatch | `...test_valid_planning_run_reaches_identity_verified_dispatch` | 0 |
| acceptance-test-dispatch-conflict-fails-closed | `...test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts` | 0 |
| acceptance-test-contract-consistency-matching-plan-and-schema2-pass | `...test_matching_plan_and_schema2_sheet_pass` | 0 |
| acceptance-test-strict-test-ref-placement-documented | `...test_references_task_design_documents_test_ref_placement_and_position_rules` | 0 |

**8/8 PASS，全部 exit 0。**

## J. 全量测试

见 E.1：`Ran 285 tests` / `OK`，与执行者最终态一致。

## K. 端到端验证

1. `task validate docs/tasks/test-ref-narrowing-followup.md` → `{"status":"pass","errors":[]}`，exit 0。**新规则不误伤本任务自己。**
2. `gate pre-merge .pipeline/test-ref-narrowing-followup --task-id test-ref-narrowing-followup` → `{"status":"blocked", errors:["missing review-report.md","missing final-check.md","missing reviewer-result.json","missing final-result.json"]}`，exit 3。**预期 blocked**（此刻只有 executor 一份）。注意：实测只缺 4 项，**不含** `missing executor-report.md` / `missing executor-result.json`（见 L.4）。
3. `freshness . .pipeline/... --result .../executor-result.json` → `status: pass`，`errors: []`，`observed.evidence_only: true`，`product_head: 5a41b87...`，`changed_paths` 仅两个证据文件。**通过。**

## L. 证据文件合规性

### L.1 目录内容与大小

```
17698  .pipeline/test-ref-narrowing-followup/executor-report.md
 6980  .pipeline/test-ref-narrowing-followup/executor-result.json
```

### L.2 `git ls-files` 与 `.log`

```
.pipeline/test-ref-narrowing-followup/executor-report.md
.pipeline/test-ref-narrowing-followup/executor-result.json
```

`find ... -name '*.log'` 无命中。**证据目录无任何 `.log` 文件**，符合要求。

### L.3 报告格式

- `grep -c '^```pipeline-evidence'` → **1**（恰好一个）；`grep -c '^```json'` → **0**。块在文件末尾，JSON 合法。
- `executor-result.json` JSON 合法，键齐全：`acceptance, acceptance_id_format, assertions, branch, commands, evidence_refs, identity, recommendation, role, round, schema, status, task_id, unverified, worktree`。
- `role` = `executor` ✓；`status` = `READY-TO-MERGE` ∈ {PASS, READY-TO-MERGE} ✓。
- `commands[]` 每条均有非空 `command`、整数 `exit_code`、`evidence_ref`。非零 exit_code 两条：`(after removing narrowing, before migration)` exit 1 已显式声明 `expected_exit_code: 1`；`gate pre-merge` exit 3 已显式声明 `expected_exit_code: 3`。**合规。**

### L.4 执行者自曝的不一致（独立评估）

执行者报告 §11.2 原文记录 gate 结果为：

> `{"status":"blocked","errors":["missing executor-report.md","missing review-report.md","missing final-check.md","missing executor-result.json","missing reviewer-result.json","missing final-result.json"]}`

本审查实测（执行者两份证据已落盘并提交后）：

> `errors: ["missing review-report.md","missing final-check.md","missing reviewer-result.json","missing final-result.json"]`

即执行者当时跑 gate 时，`executor-report.md` / `executor-result.json` **尚未落盘**，故多报这两项；现在它们已存在，不再报缺。

**判定：这是证据时序瑕疵，不是记录错误。** gate 命令在证据文件写入之前执行，其输出在当时是真实的；执行者据实记录了当时的输出，而非虚构。差异完全由「命令先于证据落盘」这一时序解释，机器 `commands[]` 里的 gate 记录本身未声明缺失清单，故无矛盾。

**严重性：低。** 影响范围：
- 不影响任何一条 acceptance（8 条 acceptance 均不依赖 gate 输出）；
- 不影响交付可信度：gate 在 executor 阶段本就**预期 blocked**，且缺 review/final 是正确结论；
- 唯一后果是 §11.2 的散文里多列了两项，属**陈旧快照**。

**建议**（非阻塞）：若追求报告与最终态一致，可在 §11.2 注明「该输出为证据落盘前快照；落盘后实测仅缺 review/final 四项」。

### L.5 `executor-result.json` 核验

- JSON 合法；`identity` = `{"product_head":"5a41b87b...","head":"5a41b87b..."}`。
- **注意**：审查时实际 HEAD 为 `04dc81b`（证据提交）。`product_head` 记录产品代码提交 `5a41b87` 正确，但 `identity.head` 亦写为 `5a41b87` 而非 `04dc81b`。属**轻微不精确**：executor-result 在其自身被提交前撰写，彼时 HEAD 为 `5a41b87`；证据提交 `04dc81b` 只新增证据文件，`product_head` 不变，故对 `product_head` 语义无影响。**非阻塞。**
- `acceptance` 8 条全部 `PASS` / `exit_code 0`；`unverified` = `["independent review (reviewer-result.json)","final check (final-result.json)","merge to main"]`，如实列出未完成项。

### L.6 执行者是否如实报告失败或未完成项

§15 声明「无失败或未完成项」，并**主动披露**迁移中一度出现 2 条残留 FAIL（`_dispatch_inputs` 与 CLI 边界用例的 plan.resources 用了别名 `test-resource`，`compare_task_plan_contract` 不传 project_facts 无法解析，后改为字面路径修正）。该自曝与 diff 中 `plan.resources` 使用字面 `tests/test_cli.py` 而 project.resources 使用 `{'id':'test-resource'}` 的形态一致，**披露属实**。§16 如实标注 `unknown-historic-41-count` 无法独立复现。**总体如实。**

### L.7 `result verify` 与状态大小写（新发现）

`references/acceptance-evidence.md` 要求 `result verify` 先通过。实测：

- 对 `executor-result.json` 跑 `result verify` → **fail, exit 2**，errors 为 `invalid status` + `acceptance 1..8 has invalid status`。
- 对 `reviewer-result.json`（小写）跑 → **pass, exit 0**。

根因（`pipeline_tools/core.py:1200`、`:1213`）：`verify_structured_result` 的顶层 `status` 只接受 `{"pass","fail","blocked","flaky"}`，每条 `acceptance[].status` 只接受 `{"pass","fail","blocked","flaky","unverified"}` —— **全部小写**。而同一份证据在 markdown 的 `pipeline-evidence` 块里（`evidence_verify` / gate）要求的是**大写** `{"PASS","READY-TO-MERGE",...}`（`core.py:364-372`、`:1670`）。两套约定并存且方向相反，执行者只满足了 gate 侧，未满足 `result verify` 侧，且未披露。

这是**产品工具的双约定**问题，不是本任务范围内的产品代码缺陷；本任务 reviewer 证据已按 `result verify` 的小写要求书写，同时保留 markdown 块的大写以满足 gate。

## M. 22 条清单完整性

见 E.4。执行者清单与实测集**逐条一致**，分布 `15 + 3 + 4` 与实测 `15 + 4 + 3` **一致**（仅排序表述不同）。**清单完整。**

---

## 与执行者自述不符之处（逐条）

1. **中间态失败数**：执行者称 22；本审查在 temp 树实测 **23**。差异原因已定位：第 23 条 `test_tracked_pipeline_evidence_contains_only_retained_names` 是 temp 树无 `.git` 的环境伪影（pristine 基线树同样失败）。在真实 worktree 内该条不失败，故执行者的 **22 是正确口径**，但其「22」的验证未在无法复现仓库依赖的 temp 树上暴露此点。**属环境口径差异，非事实性误报。**
2. **gate 缺失清单**：执行者 §11.2 列 6 项，实测 4 项（见 L.4）。**时序瑕疵。**
3. **`identity.head`**：executor-result 记 `5a41b87`，审查时 HEAD 为 `04dc81b`。**轻微不精确，非阻塞。**
4. **`result verify` 从未被执行者跑过**：`executor-result.json` 用大写状态，`result verify` 判其 fail（exit 2，L.7）。执行者自述「无失败或未完成项」未涵盖该点。**属证据格式缺陷，非阻塞。**

以上四点均**不影响**核心交付与 8 条 acceptance。

## 总体结论

**ACCEPT WITH CONDITIONS。**

理由：4 个 operation 全部落地并独立复现——收窄豁免确已删除（C.2）、判定无条件（C.3）、`_shares_test_root` 未动（C.4）、无额外放宽（C.5）、22 条 fixture 迁移零断言削弱（D）、红绿转换独立复现为 22 条真实收窄失败（E）、文档两处收窄均处理且无残余（F）、文档测试两种断言齐备且有区分力（G）、8 条 acceptance 全绿（I）、全量 285 OK（E.1）、端到端三项符合预期（K）、证据合规且无 `.log`（L）。

Conditions（非阻塞，交主代理终审裁决）：
- C1：§11.2 gate 输出为陈旧快照，建议在最终检查中注明实际缺项（L.4）。
- C2：executor-result `identity.head` 与最终 HEAD 不一致，属证据撰写时序，建议终审以 `product_head=5a41b87` 为产品基线（L.5）。
- C3：`_shares_test_root`（`:669`）成为死代码，本任务明确「保留未动」，是否后续清理不由本任务决定（见 C 节 C.4）。
- C4：`executor-result.json` 的 `status` 用大写（`READY-TO-MERGE`/`PASS`），而 `result verify` 只接受小写（`pass`/`fail`/`blocked`/`flaky`），故该文件直接判 fail（L.7）。`reviewer-result.json` 已改用小写并通过；markdown 的 `pipeline-evidence` 块仍保留大写，因为 gate pre-merge 要求那里的 `PASS`/`READY-TO-MERGE`。对本任务产品代码非阻塞，但**执行者证据不是 result-verify 干净的**。

## 需主代理终审裁决项

1. 上述 C1–C3 是否接受为可合并状态。
2. `unknown-historic-41-count`（任务单已记 non_blocking）本任务无法独立复现，是否维持 non_blocking。

## 无法确定项

- `unknown-historic-41-count`：终审记录 41/22 vs 37/18 的历史差异无法在本任务独立复现；本轮进程内实测中间态为 22 条收窄失败，与 22 一致。

```pipeline-evidence
{"schema":1,"task_id":"test-ref-narrowing-followup","worktree":".worktrees/test-ref-narrowing-followup","branch":"test-ref-narrowing-followup","role":"reviewer","round":1,"status":"PASS","commands":[{"command":"git log --oneline -5; git worktree list --porcelain; git status --short","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git diff f0e5b7c HEAD --name-status","exit_code":0,"evidence_ref":"review-report.md"},{"command":"sha256sum docs/tasks/test-ref-narrowing-followup.md; git show f0e5b7c:docs/tasks/test-ref-narrowing-followup.md | sha256sum","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git diff f0e5b7c HEAD -- pipeline_tools/planning.py","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git show f0e5b7c:pipeline_tools/planning.py | grep -n 'if not claimed'","exit_code":0,"evidence_ref":"review-report.md"},{"command":"grep -n 'if not claimed' pipeline_tools/planning.py","exit_code":1,"expected_exit_code":1,"evidence_ref":"review-report.md"},{"command":"git diff f0e5b7c HEAD -- tests/test_cli.py tests/test_planning_dispatch_integration.py tests/test_task_plan_contract_consistency.py","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git diff f0e5b7c HEAD -- tests/ | grep -E '^[+-].*(skip|expectedFailure|assert)' (only 5 new doc-test assertions)","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests (final HEAD)","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests (temp tree: baseline f0e5b7c + HEAD planning.py only)","exit_code":1,"expected_exit_code":1,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules (temp tree with narrowed wording reintroduced)","exit_code":1,"expected_exit_code":1,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_planning_generate_task_sheets_cli_lifecycle","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json task validate docs/tasks/test-ref-narrowing-followup.md","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/test-ref-narrowing-followup --task-id test-ref-narrowing-followup","exit_code":3,"expected_exit_code":3,"evidence_ref":"review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/test-ref-narrowing-followup --result .pipeline/test-ref-narrowing-followup/executor-result.json","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git ls-files .pipeline/test-ref-narrowing-followup/; find .pipeline/test-ref-narrowing-followup/ -name '*.log'","exit_code":0,"evidence_ref":"review-report.md"},{"command":"grep -c '^```pipeline-evidence' .pipeline/test-ref-narrowing-followup/executor-report.md","exit_code":0,"evidence_ref":"review-report.md"}],"assertions":["Narrowing exemption removed: baseline planning.py line 703 'if not claimed' is absent in HEAD; grep for 'claimed' returns no match.","_validate_test_ref_placement now judges unconditionally with 'if any(_covers_path(item, path) for item in allowed_paths): continue'; _shares_test_root (planning.py:669) is untouched dead code and _covers_path has no new permissive branch.","Call site planning.py:1157 is unchanged and still guarded by 'if task_allowed_paths:'.","Zero assertion/skip/expectedFailure lines changed in the three fixture files; tests/test_planning.py is untouched; only fixture resources/allowed_paths input data changed (mechanical derivation).","Temp-tree reproduction (baseline f0e5b7c + HEAD planning.py only) yields 23 failures: 22 genuine narrowing failures distributed 15/4/3 across test_planning_dispatch_integration.py / test_cli.py / test_task_plan_contract_consistency.py, plus 1 repository-dependent artifact (test_tracked_pipeline_evidence_contains_only_retained_names, 'not a git repository') which also fails on the pristine baseline temp tree.","Final HEAD full suite: Ran 285 tests, OK, 0 failures.","references/task-design.md section '### `test_ref` 的位置规则' now states the unconditional rule; the same-directory-tree qualifier is removed and the exemption sentence is deleted; grep for 不主张归属/提出归属主张/位置校验不生效 returns zero hits.","The doc-compliance test carries both a positive unconditional assertion and negative exemption assertions, retains all pre-existing assertions, passes at exit 0, and is discriminating: a mutated doc copy reintroducing the exemption wording fails it at exit 1.","All 8 acceptance tests pass with exit_code 0.","task validate on the task's own sheet passes (exit 0); gate pre-merge is blocked (exit 3) listing only missing review-report.md, final-check.md, reviewer-result.json, final-result.json; freshness passes with evidence_only true and no errors.","Evidence directory holds exactly executor-report.md and executor-result.json, contains no .log file, and executor-report.md has exactly one pipeline-evidence fenced block with a valid JSON payload.","Executor self-disclosed gate inconsistency is an evidence-timing artifact (gate ran before evidence landed); executor-result identity.head records 5a41b87 while HEAD at review is 04dc81b; both are non-blocking.","reviewer-result.json passes result verify with lower-case statuses (exit 0); executor-result.json fails result verify because it uses upper-case statuses, which the validator rejects."],"evidence_refs":["review-report.md","reviewer-result.json","executor-report.md","executor-result.json"],"unverified":["unknown-historic-41-count (historical 41/22 vs 37/18 discrepancy could not be independently reproduced)","final check (final-result.json)","merge to main"]}
```
