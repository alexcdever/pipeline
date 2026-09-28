# status-vocabulary-unification：主代理终审报告

## 任务身份

- task_id：`status-vocabulary-unification`
- 任务类型：`prerequisite`（planning-time 机器契约检查，无用户可观察链路）
- 基线：`82d4827`（冻结任务单）；worktree：`D:/Projects/Skills/pipeline/.worktrees/status-vocabulary-unification`；branch：`status-vocabulary-unification`
- 终审角色：`main-final`，round 1
- 结论：**ACCEPT WITH CONDITIONS**（唯一条件见第七、八节：`freshness` 因修正提交移动 `product_head` 而报漂移，需人类裁决；不修改任何历史产物）

本报告不引用任何已删除的原始日志（`goal.md:51`）；全部 `commands[].evidence_ref` 与 `evidence_refs` 均为本报告与 `final-result.json` 两个裸文件名。

## 一、独立复核的核心事实（不抄任何摘要）

| 项 | 实测 |
|---|---|
| 提交链 | `548a1ae` → `7bcebcc` → `0b5c8fb` → `92ef248` → `82d4827`（基线）→ `6d3dc6c` |
| `git diff 82d4827 HEAD --name-status` | 10 个 `.pipeline/metrics/*.json`（A）+ 4 个证据文件（A：executor 2 + reviewer 2）+ 8 个产品/测试/文档文件（M） |
| 任务单 sha256 | `97e0c80b755ee75084e1b41f2ea1a6698a8739f1f295ce65ee317304835899a2`，与派发一致，冻结任务单未改 |
| 证据目录 `git ls-files` | 恰 4 个（executor-report.md / executor-result.json / review-report.md / reviewer-result.json），无 `.log`、无 `freshness.json` |
| `origin/main..HEAD` | 终审提交前 **60**；+ 本次终审 1 = **61**（派发 56 + 执行者 2 + 审查者 1 + 修正 1 + 终审 1），一致 |
| `git diff --check` | exit 0（无空白错误，与 `cmd_validate` 的检查口径一致） |

**6 条 acceptance 逐条实跑**（`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`，全部 `Ran 1 test ... OK`，**exit_code 0**）：

1. `tests.test_evidence.EvidenceTests.test_gate_accepts_normalized_report_statuses` → 0
2. `tests.test_evidence.EvidenceTests.test_result_verify_accepts_normalized_result_statuses` → 0
3. `tests.test_cli.CLITests.test_result_verify_cli_accepts_final_role` → 0
4. `tests.test_evidence.EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions` → 0
5. `tests.test_evidence.EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report` → 0
6. `tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_document_one_status_vocabulary` → 0

**全量**：`python -m unittest discover -s tests` → **`Ran 294 tests in 191.760s`，`OK`，exit 0**。基线 285，净增 9 条（6 契约 + 2 防退化 + 1 reviewer 回归）。与执行者所报一致。

## 二、任务 1：修正提交是否彻底

修正提交 `548a1ae` 只做两件事：删除重复方法定义、更正报告计数。

1. **重复方法已消失**：`grep -c "def test_references_document_one_status_vocabulary"` = **1**（实跑）。
2. **无新重名**：`grep -c "def test_"` = **19**；用正确字符类 `def test_[A-Za-z0-9_]+` 做 `sort | uniq -d` → **空**，无重名方法。
   - 注意：任务书中给的 `grep -o "def test_[a-z_]*"` 因字符类**不含数字**，会把 `test_schema2_rejects...` 截断成 `def test_schema` 而报出**假重复**。用含数字的字符类复核后无重复。
3. **保留的那份断言更强**：保留的是第 61 行那份，比被删的第 70 行那份**多一条** `self.assertIn("pass", reference)`，是严格超集。删弱留强正确；若删强留弱会静默丢失「文档明确写出规范小写 `pass`」的校验。
4. **全量数字未变**：删除重复前后均为 **294**。同名方法在 Python 类体内后者覆盖前者，`unittest` 从来只收集 1 个，删重复不改变计数——执行者的自我纠错（见第三节 3）判断正确。

## 三、任务 2：两处执行者自述不实 + 一处诚实自我纠错

1. **「新增 9 条测试」不实（已修正）**：`test_references_document_one_status_vocabulary` 在 `tests/test_acceptance_id_and_template_compliance.py` 被**定义两次**（原第 61、70 行），实为 8 条独立 + 1 条重复。`548a1ae` 删除了较弱的一份，现只余 1 处定义。
2. **gate errors 多报（已修正）**：执行者初版报告称 gate 缺 **6 件**产物；审查者实测为 **4 条**（`review-report.md`、`final-check.md`、`reviewer-result.json`、`final-result.json`）。终审实测：在三份报告尚未齐备时 gate 恰报 **2 条**（`missing final-check.md`、`missing final-result.json`），与执行者修正后的「2 条」一致。

**判断：这是证据时序问题，不是记录习惯问题，也不是伪造。** 6 件是 gate 在 executor 证据落盘**之前**运行的输出——当时证据目录为空，数字在那一刻**真实**；问题在于把「运行中途的输出」当作「终态」写入报告，此后证据继续落盘而报告未同步。**这已是本会话第三次同类问题**（前两个任务的执行者也记了过期的 gate 输出）。

**流程改进建议**：`gate`/`freshness` 的输出应在报告中标注**运行时刻 + 当时的证据目录状态**，或在全部证据冻结后**重跑再记录终态**；条件允许时让工具在输出中直接带一个「证据目录文件清单/时间戳」字段，使「中���输出」无法冒充终态。

3. **一处诚实自我纠错（与上述两处性质不同）**：执行者在修正时一度把「9 条 / 294」改成「8 条 / 293」，随后**自己发现推理错误**（同名方法本就只被收集一次）并**回退**为「9 条 / 294」，并在报告第十二节第 3 条完整记录了这次错误的更正本身。这是**主动纠错 + 如实留痕**，与「把过期输出当终态」是不同性质，应予肯定。终审实测 294 支持该回退正确。

## 四、任务 3：四个 C4 类问题逐项确认（代码 + 行号）

全部落在 `pipeline_tools/core.py`（行号为 HEAD）：

1. **markdown 侧大小写归一**：`REPORT_STATUSES`（`core.py:34`）+ `normalize_status`（`core.py:58`）；`evidence_verify` 用它校验报告块状态（`core.py:457`）。
2. **JSON 侧大小写归一**：`RESULT_STATUSES`（`core.py:37`）、`ACCEPTANCE_STATUSES`（`core.py:38`）；用于 `verify_structured_result` 的顶层状态（`core.py:1235`）与逐条 acceptance 状态（`core.py:1248`）。
3. **遗留值 `pass_with_conditions` / `PASS_WITH_CONDITIONS` → `pass`**：`LEGACY_STATUS_ALIASES = {"pass_with_conditions": "pass"}`（`core.py:40`），在 `normalize_status` 内先折叠（`core.py:69`：`key = LEGACY_STATUS_ALIASES.get(key, key)`），再按大小写/`-`与`_` 等价匹配。
4. **`result verify` 的 final role**：`RESULT_ROLE_ALIASES = {"main": "main-final", "final": "main-final"}`（`core.py:41`）+ `resolve_result_role`（`core.py:76`）；用于角色比对（`core.py:1233`）；CLI `--role` choices 含 `final`（`pipeline_tools/__main__.py:350`）。

**归一化落点共六处**（`core.py` 五处 + `reconcile.py` 一处）：`core.py:457`、`1235`、`1248`、`1705`（pre-merge 门）、`1707`（post-merge 门）；`reconcile.py:11` 导入、`reconcile.py:88` 的 `direct_pass` 判定。**`planning.py` 另有三处复用**：`2095`、`2115`、`2136`（外加 `2131` 的角色比对），导入见 `planning.py:33-34`。六处校验点确实全部走归一。

## 五、任务 4：闸门未放宽的最终确认（三个反例 + 对照）

用系统 temp 构造，全部**独立实跑**：

| 反例 | 结果 |
|---|---|
| 机器结果 JSON 顶层 `status:"maybe"`（未知值） | `result verify` → `errors=["invalid status"]`，**exit 2**，status `fail` |
| acceptance 条目 `status:"sorta"`（未知值） | `result verify` → `errors=["acceptance 1 has invalid status"]`，**exit 2** |
| markdown 报告块 `status:"WEIRD_STATUS"`（未知值） | `evidence_verify` → `errors=["executor-report.md status is invalid", ...]` |

**三项均仍判 invalid，无一被接受，闸门未放宽。**（若任一被接受，本终审即停并上报；未触发。）

**词表常量与改前一致**：`git show 82d4827:pipeline_tools/core.py` 中的字面集合为 `{"pass","fail","blocked","flaky"}`（结果）、`{"pass","fail","blocked","flaky","unverified"}`（acceptance）、`{"PASS","READY-TO-MERGE"}` / `{"PASS","READY-TO-MERGE","MERGED"}`（门）——与 HEAD 的 `RESULT_STATUSES` / `ACCEPTANCE_STATUSES` / `PRE_MERGE_REPORT_STATUSES` / `POST_MERGE_REPORT_STATUSES` **逐项相同**；本次改动是把字面集合提为常量并加读取侧归一，**成员未增删**。`executor` / `reviewer` 未被放宽（仅新增 `final` 作为合法入参，且映射到既有的 `main-final`）。

**对照（正向）**：`pass_with_conditions` 与 `PASS_WITH_CONDITIONS` → `result verify` **pass / exit 0**；`--role final` 对 `role:"main-final"` 的结果 → **pass / exit 0**；`executor-result.json`（role executor）与 `reviewer-result.json`（role reviewer）→ 均 **pass / exit 0**。

## 六、执行与审查链路确认

完整链路成立：**执行（`92ef248` + 证据 `0b5c8fb`）→ 独立审查 ACCEPT WITH CONDITIONS（`7bcebcc`）→ 授权修正（`548a1ae`）→ 主代理终审（本次）**。审查者以独立上下文复核并实证 6/6、未知值仍 invalid、历史产物哈希一致、294 OK、无循环导入；其唯一条件「删除重复方法」已被 `548a1ae` 落实并经本终审复核。执行者的修正未触碰任何产品逻辑，只删死代码并更正报告计数。

## 七、与派发预测不符之处（必须记录）

**`freshness` 实测为 `blocked`，而非派发预期的 `pass`。**

实跑 `python -m pipeline_tools --format json freshness . .pipeline/status-vocabulary-unification --result .pipeline/status-vocabulary-unification/executor-result.json`：

- `status: blocked`，`errors: ["product/test HEAD drifted"]`，`observed.evidence_only: false`，exit 3。
- `observed` 显示：`head=548a1ae`、`product_head=92ef248`，`changed_paths` 含 `tests/test_acceptance_id_and_template_compliance.py`。

**成因**：`executor-result.json` 记录的 `product_head` 为 `92ef248`，但修正提交 `548a1ae` 修改了 `tests/`（非证据路径），使 HEAD 上最后一个「改非证据文件」的提交变为 `548a1ae`，与记录的 `92ef248` 不再相等，故判漂移。这是**修正动作本身的真实副作用**，不是产品缺陷，也不是伪造。

**为什么 gate 仍可 pass**：`gate_check` 只调 `evidence_verify` + plan 校验 + `_machine_result_errors`，**不**调 `evidence_freshness`（见 `core.py` 中 `gate_check` 实现）。因此 `gate` 与 `freshness` 是两个独立闸门；gate 绿不代表 freshness 绿。

**我没有做的事**：未修改 `executor-result.json` 的 `product_head`（历史产物受硬性约束保护），未通过改契约/放宽断言来掩盖漂移，未合并。

## 八、需人类裁决项

1. **`freshness` 漂移是否可接受**：`product_head` 由 `92ef248` 前移到 `548a1ae` 是**被授权的修正**（删除重复测试）导致的必然结果。可选项：(a) 认定修正合法、接受该漂移，人工记录「product_head 前移到 548a1ae」；(b) 要求重出执行者证据并把 `product_head` 更新为 `548a1ae`（会改动历史产物，需人类明确授权）。**这是本任务唯一实质条件。**
2. **是否合并**：合并是**人类开发者**的动作（`goal.md:26`）。本终审不合并、不 push、不 checkout main、不删 worktree。
3. **流程改进是否落地**：第三节 2 的「gate 输出记录时刻/证据状态或证据冻结后重跑」建议是否纳入规范。

## 九、未验证项

- **合并到 main、push、worktree 删除**：未执行（按硬性约束）。
- **`freshness` 的 `pass`**：未取得（实测 `blocked`，原因见第七节）。
- **`resolve_result_role` 的 `main` 别名在真实终审链路上的端到端行为**：仅有静态调用点与 `final` 别名的实测；`main` 别名未单独跑端到端。
- **`.pipeline/metrics/` 跨任务增长趋势**：未验证。
- 本终审未修改 `pipeline_tools/**`、`tests/**`、`references/**`、`templates/**`、冻结任务单及执行者/审查者三份历史产物；未删除 `.pipeline/metrics/` 任何文件；唯一删除的是本次 `freshness` 运行生成的 `freshness.json`（已删，证据目录现为 4 个文件）。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "status-vocabulary-unification",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/status-vocabulary-unification",
  "branch": "status-vocabulary-unification",
  "role": "main-final",
  "round": 1,
  "status": "READY-TO-MERGE",
  "commands": [
    {"command": "python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_normalized_report_statuses", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_evidence.EvidenceTests.test_result_verify_accepts_normalized_result_statuses", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_cli.CLITests.test_result_verify_cli_accepts_final_role", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_evidence.EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_document_one_status_vocabulary", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "grep -c 'def test_references_document_one_status_vocabulary' tests/test_acceptance_id_and_template_compliance.py", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "grep -oE 'def test_[A-Za-z0-9_]+' tests/test_acceptance_id_and_template_compliance.py | sort | uniq -d", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "sha256sum docs/tasks/status-vocabulary-unification.md", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m pipeline_tools --format json result verify .pipeline/status-vocabulary-unification/executor-result.json --task-id status-vocabulary-unification --role executor", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m pipeline_tools --format json result verify .pipeline/status-vocabulary-unification/reviewer-result.json --task-id status-vocabulary-unification --role reviewer", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m pipeline_tools --format json result verify <tmp>/bad-result.json --task-id status-vocabulary-unification --role executor", "exit_code": 2, "expected_exit_code": 2, "evidence_ref": "final-check.md"},
    {"command": "python -m pipeline_tools --format json result verify <tmp>/bad-acceptance.json --task-id status-vocabulary-unification --role executor", "exit_code": 2, "expected_exit_code": 2, "evidence_ref": "final-check.md"},
    {"command": "python -m pipeline_tools --format json freshness . .pipeline/status-vocabulary-unification --result .pipeline/status-vocabulary-unification/executor-result.json", "exit_code": 3, "expected_exit_code": 3, "evidence_ref": "final-check.md"},
    {"command": "python -m pipeline_tools --format json gate pre-merge .pipeline/status-vocabulary-unification --task-id status-vocabulary-unification --branch status-vocabulary-unification", "exit_code": 0, "evidence_ref": "final-check.md"}
  ],
  "assertions": [
    "all six contract acceptance tests run green with exit_code 0",
    "the full suite is Ran 294 tests, OK, exit 0, against a baseline of 285",
    "the duplicated test method is gone: grep -c returns 1 and no duplicate method names remain",
    "the preserved test definition is the stronger one, carrying an extra assertIn for the lowercase pass spelling",
    "removing the shadowed duplicate left the collected count at 294, confirming unittest had always counted the name once",
    "an unknown machine-result top-level status is still rejected: result verify returns invalid status and exit 2",
    "an unknown acceptance status is still rejected: result verify returns acceptance 1 has invalid status and exit 2",
    "an unknown markdown report status is still rejected by evidence_verify",
    "the status vocabulary constants match the baseline literal sets member for member; executor and reviewer were not widened",
    "legacy pass_with_conditions and PASS_WITH_CONDITIONS normalize to pass, and --role final maps onto main-final",
    "the frozen task sheet sha256 is unchanged from commit 82d4827",
    "the three historical evidence artifacts and the two machine results still verify as pass",
    "freshness reports blocked with product/test HEAD drifted because the authorised correction commit moved product_head off the recorded 92ef248",
    "the git subject line is 62 characters, within the 72 character limit"
  ],
  "evidence_refs": ["final-check.md", "final-result.json"],
  "unverified": [
    "merge to main, push, and worktree removal (human-only actions)",
    "freshness reaching pass (measured blocked; needs human adjudication of the product_head drift)",
    "the main alias of resolve_result_role on a real final-check chain",
    "cross-task metrics growth trend"
  ],
  "identity": {
    "product_head": "548a1ae8ba91494b51b0f53c8aec61485a580d60",
    "head": "548a1ae8ba91494b51b0f53c8aec61485a580d60",
    "baseline": "82d4827"
  },
  "verdict": "ACCEPT WITH CONDITIONS"
}
```