# 主代理终审报告：test-ref-narrowing-followup

## 0. 任务身份

- task-id：`test-ref-narrowing-followup`
- 类型：`prerequisite`（规划期机械底座，无用户可观察完成）
- worktree：`D:\Projects\Skills\pipeline\.worktrees\test-ref-narrowing-followup`
- branch：`test-ref-narrowing-followup`
- 基线：`f0e5b7c`（冻结任务单）
- 终审时 HEAD：`0100f52`
- 轮次：1

## 1. 任务 1：C4 的正式裁定

### 1.1 双约定确实存在（独立核验）

markdown 侧（gate 用，要求大写）：

- `pipeline_tools/core.py:364-372`：`valid_statuses = {` / `"PASS",` / `"FAIL",` / `"BLOCKED",` / `"FLAKY",` / `"EXPLORATORY_ONLY",` / `"READY-TO-MERGE",` / `"MERGED",` / `}`。
- `pipeline_tools/core.py:422`：`if value.get("status") not in valid_statuses:` —— `evidence_verify` 读取 pipeline-evidence 块时的状态校验。
- `pipeline_tools/core.py:1670`：`if status not in {"PASS", "READY-TO-MERGE"}:` —— `gate_check` 的 pre-merge 闸门。

JSON 侧（`result verify` 用，要求小写）：

- `pipeline_tools/core.py:1200`：`if value.get("status") not in {"pass", "fail", "blocked", "flaky"}:`
- `pipeline_tools/core.py:1213`：`if item.get("status") not in {"pass", "fail", "blocked", "flaky", "unverified"}:`

两套词表方向相反且并存：同一份产物在 markdown 块里必须大写，在 JSON 机器结果里必须小写。

### 1.2 `0100f52` 修复核验

`git show --stat 0100f52`：新增 1 个 metrics 文件、`executor-report.md` +21 行（补记第 17 节）、`executor-result.json` 18 行改动。diff 逐行核对，只有大小写：

- 顶层 `"status": "READY-TO-MERGE"` → `"pass"`
- 8 条 `acceptance[].status`：`"PASS"` → `"pass"`

`identity`、`acceptance` 条目集合、`commands`、`assertions`、`evidence_refs`、`unverified` 均未改。语义未变。

### 1.3 实跑结果

- `result verify executor-result.json --role executor` → `{"status":"pass","errors":[]}`，exit 0
- `result verify reviewer-result.json --role reviewer` → `{"status":"pass","errors":[]}`，exit 0
- `gate pre-merge` → exit 3，`errors:["missing final-check.md","missing final-result.json"]` —— markdown 侧未被破坏

### 1.4 性质判定

执行者只满足了 gate/markdown 侧（大写），未满足 `result verify` 侧（小写），而原报告称「无失败或未完成项」，未涵盖此点。这是证据格式契约未对齐导致的机器结果不可校验，属**中等严重性**：产品代码无缺陷（全量 285 全绿、8/8 验收全绿），但机器可读结果在被独立校验前处于 fail 状态，且执行者未自查。已由 `0100f52` 修复并复核。

### 1.5 工具链张力（另开单建议）

`result verify`（小写）与 gate 证据块（大写）方向相反，属**工具链既有张力**，不在本任务范围。建议另开单统一两份状态词表。

## 2. 任务 2：三处轻量瑕疵

### 2.1 gate 缺失清单 6 项 vs 实测 4 项

`executor-report.md:157` 记录 gate 输出 6 项缺失（含 `executor-report.md`、`executor-result.json`）。核验：该 gate 命令在 executor 证据落盘之前执行，输出在当时真实——若报告已存在，它不会被列为 missing。故为**证据时序瑕疵，非记录错误**。

### 2.2 `identity.head` = `5a41b87` 而审查时 HEAD = `04dc81b`

`executor-result.json` 的 `identity.product_head`/`head` 均为 `5a41b87`。写入 identity 会改变 HEAD，这是已知的自指特性；`reviewer-result.json` 的 `identity.basis` 已记录该约定。**可接受，非阻塞。**

### 2.3 `_shares_test_root` 死代码

`git grep _shares_test_root HEAD`：代码引用仅 `pipeline_tools/planning.py:669`（定义本身）；其余命中全部落在 `.pipeline/**` 历史证据（数据，非代码）。函数确为死代码。任务单明确「保留未动」，**清理另开单，本任务不动。**

## 3. 任务 3：`unknown-historic-41-count`

审查者已解释 41/22 vs 37/18 为 subprocess 级 vs 进程内计数差异；本轮进程内实测中间态为 22 条，与 22 一致，41 无法独立复现。任务单已记 `non_blocking`。**维持 non_blocking，无需进一步调查。**

## 4. 执行与审查阶段确认

链路完整：执行 `5a41b87`+`04dc81b` → 独立审查 `220cd5a`（ACCEPT WITH CONDITIONS）→ C4 修复 `0100f52` → 终审（本报告）。审查者四项条件 C1-C4 均已核验：C4 已修复并复核，C1/C2/C3 记录为轻量瑕疵。

## 5. 核心事实独立复核

- 提交链：`f0e5b7c` → `5a41b87` → `04dc81b` → `220cd5a` → `0100f52`
- `git diff f0e5b7c HEAD --name-status`：6 个产品/测试/文档文件 M；11 个 metrics + 4 个证据文件 A
- 8 条验收测试逐条实跑：全部 EXIT=0
- 全量：`Ran 285 tests in 194.489s` → `OK`
- 任务单 sha256：`c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93`（与冻结值一致，字节未变）
- 抽查：`_validate_test_ref_placement` 收窄确已删除、判定无条件；`_covers_path` 未改；`references/task-design.md` 两处收窄均已处理；文档测试正/负断言齐备
- `freshness`：`status=pass`，`errors=[]`，`evidence_only=true`
- 证据目录：4 个已有 + 本报告两份 = 6

```pipeline-evidence
{"schema":1,"task_id":"test-ref-narrowing-followup","worktree":".worktrees/test-ref-narrowing-followup","branch":"test-ref-narrowing-followup","role":"main-final","round":1,"status":"PASS","commands":[{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests (final HEAD)","exit_code":0,"evidence_ref":"final-check.md"},{"command":"8x python -m unittest <acceptance command_ref> (loop over contract acceptance_tests)","exit_code":0,"evidence_ref":"final-check.md"},{"command":"python -m pipeline_tools --format json result verify .pipeline/test-ref-narrowing-followup/executor-result.json --task-id test-ref-narrowing-followup --role executor","exit_code":0,"evidence_ref":"final-check.md"},{"command":"python -m pipeline_tools --format json result verify .pipeline/test-ref-narrowing-followup/reviewer-result.json --task-id test-ref-narrowing-followup --role reviewer","exit_code":0,"evidence_ref":"final-check.md"},{"command":"python -m pipeline_tools --format json gate pre-merge .pipeline/test-ref-narrowing-followup --task-id test-ref-narrowing-followup","exit_code":3,"expected_exit_code":3,"evidence_ref":"final-check.md"},{"command":"python -m pipeline_tools --format json freshness . .pipeline/test-ref-narrowing-followup --result .pipeline/test-ref-narrowing-followup/executor-result.json","exit_code":0,"evidence_ref":"final-check.md"},{"command":"sha256sum docs/tasks/test-ref-narrowing-followup.md","exit_code":0,"evidence_ref":"final-check.md"},{"command":"python -c verify_structured_result(final-result.json, test-ref-narrowing-followup, main-final)","exit_code":0,"evidence_ref":"final-result.json"}],"assertions":["C4 dual convention confirmed independently: core.py:364-372 valid_statuses is upper-case (markdown/gate) while core.py:1200/1213 accepts only lower-case (result verify).","0100f52 changes only the letter case of status fields in executor-result.json; no identity, acceptance-set, commands, assertions or evidence_refs change.","result verify passes for executor-result.json and reviewer-result.json at exit 0 with lower-case statuses.","gate pre-merge now reports only missing final-check.md and final-result.json (exit 3), so the upper-case markdown side is intact.","Full suite: Ran 285 tests in 194.489s, OK.","All 8 acceptance tests exit 0.","Frozen task sheet sha256 unchanged: c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93.","_validate_test_ref_placement now judges unconditionally; _covers_path unchanged; _shares_test_root is untouched dead code.","freshness: status pass, errors [], evidence_only true."],"evidence_refs":["final-check.md","final-result.json"],"unverified":["unknown-historic-41-count: 41/22 vs 37/18 historical discrepancy could not be independently reproduced","merge to main (human developer action)"]}
```