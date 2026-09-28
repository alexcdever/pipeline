# 执行者报告：status-vocabulary-unification

## 一、任务身份

- task-id：`status-vocabulary-unification`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\status-vocabulary-unification`
- branch：`status-vocabulary-unification`
- baseline：`82d4827`（冻结任务单提交）
- 角色：executor，round 1
- 执行提交：`92ef2489ed5fb89862652c0d0767b0bcb332b3b0`
- 证据提交：本报告与其后的 `executor-result.json`（在上述执行提交之后）

## 二、共享归一函数的设计

### 放置位置

放在 `pipeline_tools/core.py` 模块级，紧邻既有的模块常量区，函数紧邻 `redact()` 之前定义。

理由：`core.py` 已经是 `reconcile.py` 与 `planning.py` 的共同上游（`reconcile.py` 已 `from .core import ...`，`planning.py` 已 `from .core import RETAINED_EVIDENCE_NAMES`）。若新建独立模块，`core.py` 必须反向导入它，而该新模块又需要 `core` 的常量，会形成循环导入。放在 `core.py` 是唯一无需新依赖、且不引入循环的方案。

### 常量与签名

```python
REPORT_STATUSES = ("PASS", "FAIL", "BLOCKED", "FLAKY", "EXPLORATORY_ONLY", "READY-TO-MERGE", "MERGED")
PRE_MERGE_REPORT_STATUSES = ("PASS", "READY-TO-MERGE")
POST_MERGE_REPORT_STATUSES = ("PASS", "READY-TO-MERGE", "MERGED")
RESULT_STATUSES = ("pass", "fail", "blocked", "flaky")
ACCEPTANCE_STATUSES = ("pass", "fail", "blocked", "flaky", "unverified")
LEGACY_STATUS_ALIASES = {"pass_with_conditions": "pass"}
RESULT_ROLE_ALIASES = {"main": "main-final", "final": "main-final"}

def _status_key(value: Any) -> str | None
def normalize_status(value: Any, vocabulary: tuple[str, ...]) -> str | None
def resolve_result_role(role: Any) -> Any
```

`normalize_status` 的行为：

1. 非字符串或空串 → `None`（保持 invalid）。
2. 归一化键：`strip().lower()` 且把 `-` 统一成 `_`。因此大小写与连字符/下划线差异都被吸收。
3. 先过 `LEGACY_STATUS_ALIASES`：`pass_with_conditions` / `PASS_WITH_CONDITIONS` / `Pass-With-Conditions` 一律折叠为 `pass`。
4. 在该词表内按归一化键匹配，返回**词表内的规范拼写**（不是输入原样）。
5. 匹配不到 → `None`。

关键约束「归一后不在词表内的值仍判 invalid」由第 5 点保证：`normalize_status("NOT_A_STATUS", ...) is None`，调用点据此报错。测试 `test_unknown_report_status_stays_invalid` / `test_unknown_result_status_stays_invalid` 专门钉住这条，防止退化成「什么都接受」。

「不引入第三套状态拼写」：归一化后的返回值只可能是 `REPORT_STATUSES` / `RESULT_STATUSES` / `ACCEPTANCE_STATUSES` 里的既有拼写，`pass_with_conditions` 不会成为任何一侧的规范形式。

`resolve_result_role` 与 `normalize_status` 放在同一处，因为 `final` → `main-final` 的映射同样是「读取侧归一」。

## 三、六处校验点的改前改后对照

### 1. `pipeline_tools/core.py` `evidence_verify` 的 `valid_statuses`（原 `:364-372`）

改前：

```python
    valid_statuses = {
        "PASS",
        "FAIL",
        "BLOCKED",
        "FLAKY",
        "EXPLORATORY_ONLY",
        "READY-TO-MERGE",
        "MERGED",
    }
    expected_roles = {
```

改后：局部集合整体删除，`expected_roles` 直接跟随；词表上移为模块常量 `REPORT_STATUSES`。

### 2. `pipeline_tools/core.py` `evidence_verify` 的状态判定（原 `:422`）

改前：

```python
        if value.get("status") not in valid_statuses:
            errors.append(f"{name} status is invalid")
```

改后：

```python
        if normalize_status(value.get("status"), REPORT_STATUSES) is None:
            errors.append(f"{name} status is invalid")
```

### 3. `pipeline_tools/core.py` `verify_structured_result` 顶层 `status`（原 `:1200`）

改前：

```python
    if value.get("status") not in {"pass", "fail", "blocked", "flaky"}:
        errors.append("invalid status")
```

改后：

```python
    if normalize_status(value.get("status"), RESULT_STATUSES) is None:
        errors.append("invalid status")
```

### 4. `pipeline_tools/core.py` `verify_structured_result` 的 `acceptance[].status`（原 `:1213`）

改前：

```python
        if item.get("status") not in {"pass", "fail", "blocked", "flaky", "unverified"}:
            errors.append(f"acceptance {index} has invalid status")
```

改后：

```python
        if normalize_status(item.get("status"), ACCEPTANCE_STATUSES) is None:
            errors.append(f"acceptance {index} has invalid status")
```

### 5. `pipeline_tools/core.py` `gate_check` 的 pre/post-merge 收窄（原 `:1670` / `:1672`）

改前：

```python
        if phase == "pre-merge" and name in {"executor-report.md", "review-report.md", "final-check.md"}:
            if status not in {"PASS", "READY-TO-MERGE"}:
                errors.append(f"{name} status is not mergeable")
        if phase == "post-merge" and name != "executor-report.md" and status not in {"PASS", "READY-TO-MERGE", "MERGED"}:
            errors.append(f"{name} status is not post-merge passing")
```

改后：

```python
        if phase == "pre-merge" and name in {"executor-report.md", "review-report.md", "final-check.md"}:
            if normalize_status(status, PRE_MERGE_REPORT_STATUSES) is None:
                errors.append(f"{name} status is not mergeable")
        if phase == "post-merge" and name != "executor-report.md" and normalize_status(status, POST_MERGE_REPORT_STATUSES) is None:
            errors.append(f"{name} status is not post-merge passing")
```

phase 语义未变：pre-merge 的集合仍是 {PASS, READY-TO-MERGE}，post-merge 仍是 {PASS, READY-TO-MERGE, MERGED}，只是读入时先归一。

### 6. `pipeline_tools/reconcile.py:88` 的直接通过判定

改前：

```python
from .core import evidence_freshness, evidence_readiness, evidence_verify
...
                   and all(status in {"PASS", "READY-TO-MERGE", "MERGED"} for status in statuses))
```

改后：

```python
from .core import POST_MERGE_REPORT_STATUSES, evidence_freshness, evidence_readiness, evidence_verify, normalize_status
...
                   and all(normalize_status(status, POST_MERGE_REPORT_STATUSES) is not None for status in statuses))
```

### 附带：`verify_structured_result` 的 role 判定

契约的第三与第四个缺陷同源，故一并收敛：

改前：

```python
    if value.get("role") != expected_role:
        errors.append("role mismatch")
```

改后：

```python
    if resolve_result_role(value.get("role")) != resolve_result_role(expected_role):
        errors.append("role mismatch")
```

这不是放宽：`final` 与 `main-final` 折叠到同一角色，`executor` 仍只能匹配 `executor`。

## 四、`planning.py` 三处既有归一的处理

三处**全部复用**共享函数，删除各自为政的 `.upper()` / `.lower()`：

| 位置 | 改前 | 改后 |
|---|---|---|
| `_validate_finalization_report`（原 `:2088`） | `str(value.get("status", "")).upper() in {"PASS", "READY-TO-MERGE", "MERGED"}` | `normalize_status(value.get("status"), POST_MERGE_REPORT_STATUSES) is not None` |
| `_validate_finalization_acceptance`（原 `:2108`） | `str(item.get("status", "")).lower() != "pass"` | `normalize_status(item.get("status"), ACCEPTANCE_STATUSES) != "pass"` |
| `_validate_result`（原 `:2117`/`:2130`） | `role in {expected_role, "main-final"}` + `str(value.get("status", "")).lower() == "pass"` | `resolve_result_role(...) == resolve_result_role(expected_role)` + `normalize_status(..., RESULT_STATUSES) == "pass"` |

导入从 `from .core import RETAINED_EVIDENCE_NAMES` 扩展为多行导入，新增 `ACCEPTANCE_STATUSES`、`POST_MERGE_REPORT_STATUSES`、`RESULT_STATUSES`、`normalize_status`、`resolve_result_role`。

行为差异说明：`_validate_finalization_acceptance` 原来用 `.lower() == "pass"`，会**接受** `PASS` 但不接受 `pass_with_conditions`；复用后额外接受遗留值并归一到 `pass`，这是契约要求的方向（终审证据最终化时也能读懂历史遗留值），未弱化：`PASS`/`pass` 仍通过，`FAIL` 仍不通过。

## 五、final role 的映射实现

`final` 不是靠「多一个 choice 再直传」实现的，而是走统一的角色归一：

1. `pipeline_tools/__main__.py:350` 的 choices 由 `("executor", "reviewer")` 改为 `("executor", "reviewer", "final")`。
2. `verify_structured_result` 内部用 `resolve_result_role` 把传入的 `final` 映射为 `main-final`，再与结果文件里的 `role`（`main-final`）比较。
3. `planning.py` 的 `_validate_result` 复用同一映射，原来写死的 `{expected_role, "main-final"}` 特例被删除。

映射表 `RESULT_ROLE_ALIASES = {"main": "main-final", "final": "main-final"}`：`main` 一项保留 `planning.py` 既有调用方（`finalize_evidence` 传 `expected_role="main"`）的语义，`final` 一项是本次新增的 CLI 入口。这样两个入口都收敛到同一张表。

## 六、6 条新验收测试

全部新建。前 5 条落在 `tests/test_evidence.py`（按契约 `test_ref` 要求位于 `EvidenceTests` 类内），第 3 条落在 `tests/test_cli.py`，第 6 条落在 `tests/test_acceptance_id_and_template_compliance.py`。

> **裁决后更正**：第 6 条初版被重复定义两次（第 61/70 行），较弱的一份已删除，详见第十二节。本表列举的 6 条即最终生效的 6 条。

| # | test_ref | 断言什么 |
|---|---|---|
| 1 | `EvidenceTests.test_gate_accepts_normalized_report_statuses` | markdown 侧三份报告写 `pass` / `ready-to-merge` / `Pass` 时，`evidence_verify` 无错、`gate_check(pre-merge)` 不报 status/mergeable |
| 2 | `EvidenceTests.test_result_verify_accepts_normalized_result_statuses` | JSON 侧顶层 `PASS` 与 `acceptance[].status="Pass"` 时 `verify_structured_result` 返回 `[]` |
| 3 | `CLITests.test_result_verify_cli_accepts_final_role` | `result verify --role final` 对 `role="main-final"` 的结果文件退出码 0 |
| 4 | `EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions` | JSON 侧 `pass_with_conditions`（顶层与 acceptance 同时）归一到 `pass`，返回 `[]` |
| 5 | `EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report` | markdown 侧 `PASS_WITH_CONDITIONS` 归一到 `pass`，`evidence_verify` 无错且 gate 不报 mergeable |
| 6 | `AcceptanceIdAndTemplateComplianceTests.test_references_document_one_status_vocabulary` | 文档含「归一」「pass_with_conditions」「evidence_verify」「verify_structured_result」；模板 `status` 仍为大写 `PASS` |

第 4 与第 5 条的分工：第 4 条打 JSON 侧入口 `verify_structured_result`（调用方传 `role='executor'`），第 5 条打 markdown 侧入口 `evidence_verify` + `gate_check`。

### 修复前确实红的证据

把四处实现文件临时 stash（`git stash push -- pipeline_tools/{core,planning,reconcile,__main__}.py`）后重跑 5 条行为测试：

- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_normalized_report_statuses tests.test_evidence.EvidenceTests.test_result_verify_accepts_normalized_result_statuses tests.test_cli.CLITests.test_result_verify_cli_accepts_final_role tests.test_evidence.EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions tests.test_evidence.EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report`
- 结果：`Ran 5 tests`，`FAILED (failures=5)`，退出码 **1**。
- 典型失败原因：`['executor-report.md status is invalid', 'review-report.md status is invalid', 'final-check.md status is invalid']`；`['invalid status', 'acceptance 1 has invalid status']`；`argument --role: invalid choice: 'final' (choose from executor, reviewer)`。

第 6 条（文档措辞）初版报告称「不单独取红证据」，属不完整。裁决后已补测：把 `references/acceptance-evidence.md` 与 `templates/pipeline-evidence.json` 回退到 baseline `82d4827` 后单跑该条，结果 `Ran 1 test` / `FAILED (failures=1)` / `exit 1`，`AssertionError: '归一' not found in ...`。该条同样有区分力。

另加两条防退化测试（非契约要求，用于钉住「不能变成什么都接受」）：`test_unknown_report_status_stays_invalid`、`test_unknown_result_status_stays_invalid`。它们修复前后都通过，属回归护栏而非红绿证据。

## 七、测试结果

### 针对性

命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence tests.test_cli tests.test_acceptance_id_and_template_compliance`

- 结果：`Ran 113 tests in 55.317s`，**OK**，退出码 0。

6 条契约命令逐条单跑，全部 `Ran 1 test` **OK**（`exit 0`）。

### 全量（门禁）

命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests`

- 结果：`Ran 294 tests in 215.811s`，**OK**，退出码 0。
- 基线 285，本次新增 9 条（6 条契约 + 2 条防退化 + 1 条 `test_result_verify_cli_accepts_reviewer_role`）。
- **裁决后更正（2026-09-29）**：本行一度被改为「净新增 8 条 / 全量 293」，理由是第 6 条测试被重复定义、删掉一份后计数应减一。**该更正是错的，已回退**。原因见第十二节：`test_references_document_one_status_vocabulary` 虽在 `tests/test_acceptance_id_and_template_compliance.py` 里出现两次（第 61/70 行），但 Python 类体同名方法后者覆盖前者，`unittest` 从来只收集 1 个，删除重复并不改变收集数。删除后实测全量仍为 **`Ran 294 tests ... OK`**，故「新增 9 条」「294」原本就是正确的计数。
- 未改动任何既有断言来迁就实现；无既有测试因本次改动转红。

## 八、端到端验证：修复前 vs 修复后

两份历史产物的 `result verify`，同一命令、同一文件，唯一变量是实现是否回退（`git stash` 前后）。

### `reviewer-result.json`（`status: "pass_with_conditions"`，`role: "reviewer"`）

命令：`python -m pipeline_tools --format json result verify .pipeline/evidence-retention-forward-gate/reviewer-result.json --task-id evidence-retention-forward-gate --role reviewer`

| | 退出码 | 输出 |
|---|---|---|
| 修复前 | 1 | `status: fail`，`errors: ["invalid status", "acceptance N has invalid status", ...]`（遗留值不在小写词表内） |
| 修复后 | **0** | `status: pass`，`errors: []` |

### `final-result.json`（`role: "main-final"`，`status: "pass_with_conditions"`）

命令：`python -m pipeline_tools --format json result verify .pipeline/gate-deletion-semantics/final-result.json --task-id gate-deletion-semantics --role final`

| | 退出码 | 输出 |
|---|---|---|
| 修复前 | 2 | argparse 直接拒绝：`invalid choice: 'final' (choose from executor, reviewer)`；即使换成 `--role main-final` 也会因 `pass_with_conditions` 判 `invalid status` |
| 修复后 | **0** | `status: pass`，`errors: []` |

修复前的 `final` 那份退出码是 argparse 的 2，不是结果校验的 1——这两条已在证据块中以 `expected_exit_code` 显式声明。

## 九、三份历史产物的哈希对照（证明未被触碰）

| 文件 | 基线 sha256 | 本次实测 |
|---|---|---|
| `.pipeline/gate-deletion-semantics/final-result.json` | `c8e61ee06578c5db938253d9c149c5587c9f2b7b7326b84212b0b998eed249d7` | 一致 |
| `.pipeline/evidence-retention-forward-gate/reviewer-result.json` | `1f305f8ffbdc12ad50ac4e03a6de4142a473d97c98fc90a54bf24398227ccb15` | 一致 |
| `.pipeline/evidence-retention-forward-gate/review-report.md` | `354c3d8fc725c771c3d944b235fba6201408953f62cbd9bba0bc1017d8dcba5d` | 一致 |

三者全部匹配，未被修改、未被删除、未被重写。

## 十、任务单与自检

- `task validate docs/tasks/status-vocabulary-unification.md` → `PASS`，退出码 0。
- 任务单 sha256：`97e0c80b755ee75084e1b41f2ea1a6698a8739f1f295ce65ee317304835899a2`，与 `git show 82d4827:docs/tasks/status-vocabulary-unification.md | sha256sum` **完全相同**，冻结任务单未被改动。
- `gate pre-merge .pipeline/status-vocabulary-unification --task-id status-vocabulary-unification --branch status-vocabulary-unification` → `blocked`，退出码 3。**更正**：本报告初版在此记了 6 件缺失产物，那是 gate 在 executor 证据落盘**之前**运行的输出（当时 `.pipeline/status-vocabulary-unification/` 为空目录），数字当时真实，但它不是本任务执行完毕时的状态。执行完毕后实测为 **2 条 errors**：缺 `final-check.md` 与 `final-result.json`（executor 与 reviewer 的报告/结果均已存在）——符合预期，只差主代理终审。这正是「gate 记录过期」模式：把运行中途的输出当作终态记录。
- 该 gate 曾额外报 4 条 `test_ref method is absent from tests/test_evidence.py: EvidenceTests.<方法名>`；原因是新测试初版放进了独立类 `StatusVocabularyTests`，与契约 `test_ref` 的类名不符。已把 4 条方法移入 `EvidenceTests` 并删除多余类头，复跑后该 4 条错误消失。这是一次真实的契约对齐修正，如实记录。

## 十一、改动文件清单

- `pipeline_tools/core.py`（共享归一函数 + 4 处校验点）
- `pipeline_tools/reconcile.py`（1 处判定）
- `pipeline_tools/planning.py`（导入 + 3 处复用）
- `pipeline_tools/__main__.py`（`--role` choices）
- `tests/test_evidence.py`（6 条新测试 + 1 条 reviewer 回归）
- `tests/test_cli.py`（2 条新测试）
- `tests/test_acceptance_id_and_template_compliance.py`（1 条新测试；初版重复定义，裁决后删除较弱的一份，计数由 9 更正为 8）
- `references/acceptance-evidence.md`（新增「状态词表与读取侧归一」章节）
- `templates/pipeline-evidence.json`（**未改动**：其 `status` 已是规范大写 `PASS`，符合契约「模板保持大写」要求）

未新增第三方依赖；除标准库 `json`/`re` 外未引入任何导入。

## 十二、裁决后修正记录（2026-09-29）

### 事实

独立审查者（提交 `7bcebcc`）发现两处问题，主代理裁决「打回修正」「打回更正」：

1. `tests/test_acceptance_id_and_template_compliance.py` 第 61 行与第 70 行重复定义了同一方法 `test_references_document_one_status_vocabulary`，两段都是本次新增。后者覆盖前者，第一份是死代码。**注意**：`unittest` 对同名方法只收集 1 个，因此这次重复从未让计数虚高——第六/七节「新增 9 条 / 294 tests」**是准确的**，删掉重复后实测仍是 `Ran 294 tests ... OK`。此处一度被误判为「重复导致多算一条」，是本报告自身的一次更正错误，已在第十二节第 3 条中说明。
2. 本报告第十节称 gate 缺 **6 件**产物，审查者实测只有 **4 条** errors（`review-report.md`、`final-check.md`、`reviewer-result.json`、`final-result.json`）。

### 授权来源

主代理（用户明确裁决「打回修正」「打回更正」）。

### 改了什么

1. **删除重复方法**：删除**第 61 行那一份**（较弱），保留第 70 行那一份。
   - **理由**：两份不完全相同。第 61 行那份断言 `归一`、`pass_with_conditions`、`evidence_verify`、`verify_structured_result` 与模板 `status == "PASS"`；第 70 行那份在前者基础上**多一条** `self.assertIn("pass", reference)`。后者是前者的严格超集，断言更强、覆盖更完整，故删弱留强。若删的是强的那份，会静默丢失对「文档明确写出规范小写 `pass`」这一点的校验。
2. **更正 gate 条数**：第十节由「6 件」改为实测 **2 条**（缺 `final-check.md`、`final-result.json`），并说明这是**证据时序问题**——6 件是 gate 在 executor 证据落盘前运行的输出，当时目录为空、数字真实，但被当作终态写进了报告。
3. **测试条数：更正后又回退（本报告的一次自我纠错）**。第一次更正把第六/七节及证据块中的「新增 9 条 / 294 tests」改成「净新增 8 条 / 293」，依据是「同名方法重复定义，删一份就少一条」。**该推理错误**：Python 类体内同名方法互相覆盖，`unittest` 的收集器按 `dir()` 去重，从一开始就只把这一个名字计 1 次。删除重复后实测全量输出为 `Ran 294 tests ... OK`，与删除前完全一致。故最终**回退**为「新增 9 条 / 294 tests」，原文数字正确。这次更正本身是错的，记录在此以免后续读者被误导。
4. **补充第 6 条文档测试的红证据**：初版报告称该条未单独取红证据，属不完整。本次实测：把 `references/acceptance-evidence.md` 与 `templates/pipeline-evidence.json` 回退到 baseline `82d4827` 后单跑该条 → `FAILED (failures=1)`，`exit 1`，`AssertionError: '归一' not found`。该条同样有区分力，已从「未验证项」移除。

### 这个模式值得记录

**gate 记录过期已连续三个任务出现**（本任务及前两个任务的执行者都在报告里记了过期的 gate 输出）。根因是执行者在流程中途运行 gate 并把它当作终态结论写入报告，此后证据继续变化而报告未同步。建议：gate 输出必须标注**运行时刻与当时的证据目录状态**，或在全部证据落盘后重跑再记录终态。

### 本次修正后的复核

- 重复方法计数：`grep -c` = **1**。
- 针对性测试与全量测试均 **OK**，全量 **294** 条（删除重复方法前后收集数相同，理由见第 3 条）。
- 6 条契约验收仍全绿；两份历史产物 `result verify` 仍 `pass`；三份历史产物哈希未变；冻结任务单 sha256 未变。

## 十三、未验证项

- 独立审查（`review-report.md` / `reviewer-result.json`）由审查子代理完成（`7bcebcc`）；本执行者未复核其全部结论。
- 主代理终审（`final-check.md` / `final-result.json`）未做。
- 合并到 main、push、worktree 删除均未执行（按硬性约束）。

- 未对 `.pipeline/metrics/` 的增长趋势做跨任务验证。
- 未验证 `resolve_result_role` 对 `main` 别名在真实终审链路上的端到端行为（仅有 `planning.py` 静态调用点证据）。
- 未在删除重复方法后重跑**契约要求的那 6 条**之外的全量计数比对之外的项；本条已由 `Ran 294 tests ... OK` 覆盖。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "status-vocabulary-unification",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/status-vocabulary-unification",
  "branch": "status-vocabulary-unification",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence tests.test_cli tests.test_acceptance_id_and_template_compliance",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "git stash push -- pipeline_tools/core.py pipeline_tools/planning.py pipeline_tools/reconcile.py pipeline_tools/__main__.py && PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_normalized_report_statuses tests.test_evidence.EvidenceTests.test_result_verify_accepts_normalized_result_statuses tests.test_cli.CLITests.test_result_verify_cli_accepts_final_role tests.test_evidence.EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions tests.test_evidence.EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report; git stash pop",
      "exit_code": 1,
      "expected_exit_code": 1,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/evidence-retention-forward-gate/reviewer-result.json --task-id evidence-retention-forward-gate --role reviewer",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/gate-deletion-semantics/final-result.json --task-id gate-deletion-semantics --role final",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "sha256sum .pipeline/gate-deletion-semantics/final-result.json .pipeline/evidence-retention-forward-gate/reviewer-result.json .pipeline/evidence-retention-forward-gate/review-report.md",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/status-vocabulary-unification.md",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/status-vocabulary-unification --task-id status-vocabulary-unification --branch status-vocabulary-unification",
      "exit_code": 3,
      "expected_exit_code": 3,
      "evidence_ref": "executor-report.md"
    }
  ],
  "assertions": [
    "shared normalize_status maps pass/ready-to-merge/Pass and PASS_WITH_CONDITIONS onto the canonical spelling of each side's vocabulary, and returns None for unknown values",
    "evidence_verify and gate_check accept the normalized markdown report statuses and still reject unknown ones",
    "verify_structured_result accepts normalized top-level and acceptance statuses plus the legacy pass_with_conditions value",
    "result verify --role final maps to main-final and exits 0 on the gate-deletion-semantics final-result.json",
    "all 5 behavior tests fail with exit code 1 when the implementation is stashed, and the documentation test also fails with exit code 1 when the doc change is reverted",
    "full suite is 294 tests, OK, versus a baseline of 285; removing a shadowed duplicate method definition does not change the collected count",
    "the three historical evidence artifacts keep their exact baseline sha256 values",
    "the frozen task sheet sha256 is unchanged from commit 82d4827"
  ],
  "evidence_refs": [
    "executor-report.md"
  ],
  "unverified": [
    "independent review (review-report.md / reviewer-result.json)",
    "main-agent final check (final-check.md / final-result.json)",
    "merge to main",

    "cross-task metrics growth trend"
  ]
}
```