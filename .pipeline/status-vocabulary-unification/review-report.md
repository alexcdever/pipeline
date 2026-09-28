# 审查报告：status-vocabulary-unification

独立审查者（reviewer），round 1，worktree `D:/Projects/Skills/pipeline/.worktrees/status-vocabulary-unification`，branch `status-vocabulary-unification`，基线 `82d4827`。
执行提交 `92ef248`（实现）→ `0b5c8fb`（证据），审查时 HEAD = `0b5c8fb50594ea18a1106ffc986e17c990745127`。

## 结论摘要

**ACCEPT WITH CONDITIONS**。6 条契约验收测试全部独立通过；共享归一函数的语义正确，未知值仍判 invalid；三份历史产物哈希与基线完全一致；9 项 `allowed_paths` 边界未越界。但发现 **1 个真实缺陷**（重复定义测试方法），另有 1 处执行者自述与实测不符（gate errors 条数）。缺陷不影响契约验收，但应在合并前清理。

## A. 提交与边界

- `git log --oneline -5`：`0b5c8fb`（证据）、`92ef248`（实现）、`82d4827`（冻结基线）、`6d3dc6c`、`0100f52`。链条与执行者自述一致。
- `git show --stat 92ef248`：改动 4 个产品文件 + 3 个测试文件 + 1 个 reference，另含 5 个 `.pipeline/metrics/*.json`（自动指标，允许）。
- `git show --stat 0b5c8fb`：只新增 `executor-report.md`（389 行）与 `executor-result.json`（60 行）。
- `git status --short` 与 `git status --short --untracked-files=no`：均**空**，工作树干净。
- `git diff 82d4827 HEAD --name-status` 全部改动（逐条）：
  - `A .pipeline/metrics/1790632421104554900-*.json` 等 5 个 metrics（豁免）
  - `A .pipeline/status-vocabulary-unification/executor-report.md`
  - `A .pipeline/status-vocabulary-unification/executor-result.json`
  - `M pipeline_tools/__main__.py`
  - `M pipeline_tools/core.py`
  - `M pipeline_tools/planning.py`
  - `M pipeline_tools/reconcile.py`
  - `M references/acceptance-evidence.md`
  - `M tests/test_acceptance_id_and_template_compliance.py`
  - `M tests/test_cli.py`
  - `M tests/test_evidence.py`
- **`allowed_paths` 边界（9 项）核验**：非证据改动恰为 9 项且逐一落在允许清单内（`pipeline_tools/{core,__main__,reconcile,planning}.py`、`tests/{test_evidence,test_cli,test_acceptance_id_and_template_compliance}.py`、`references/acceptance-evidence.md`）。`templates/pipeline-evidence.json` 未改（见 L 步）。**无越界**。
- `.pipeline/metrics/` 下**无任何删除**（diff 只有 `A`，无 `D`）。
- `.pipeline/status-vocabulary-unification/` 下**无 `freshness.json`**：`ls` 报 `No such file or directory`，与执行者「跑过后已删除」一致。

## B. 任务单字节未变

- `sha256sum docs/tasks/status-vocabulary-unification.md` = `97e0c80b755ee75084e1b41f2ea1a6698a8739f1f295ce65ee317304835899a2`
- `git show 82d4827:docs/tasks/status-vocabulary-unification.md | sha256sum` = `97e0c80b755ee75084e1b41f2ea1a6698a8739f1f295ce65ee317304835899a2`

**一致**，冻结任务单未被改动。

## C. 共享归一函数（核心）

`pipeline_tools/core.py:58-80` 原文：

```text
def normalize_status(value: Any, vocabulary: tuple[str, ...]) -> str | None:
    key = _status_key(value)
    if key is None:
        return None
    key = LEGACY_STATUS_ALIASES.get(key, key)
    for candidate in vocabulary:
        if _status_key(candidate) == key:
            return candidate
    return None


def resolve_result_role(role: Any) -> Any:
    if not isinstance(role, str):
        return role
    return RESULT_ROLE_ALIASES.get(role.strip().lower(), role)
```

语义逐条核验（实测）：

- 忽略大小写：`'pass' -> 'pass'`，`'PASS' -> 'pass'`（在 RESULT_STATUSES 下）。
- `-`/`_` 视为同一分隔符：`'Pass-With-Conditions' -> 'pass'`。
- 先过遗留别名表：`LEGACY_STATUS_ALIASES = {'pass_with_conditions': 'pass'}`，`'pass_with_conditions' -> 'pass'`、`'PASS_WITH_CONDITIONS' -> 'pass'`。
- 命中时返回**该词表内的规范拼写**（`return candidate`，不是输入原样）。
- 匹配不到返回 `None`：`'bogus' -> None`、`'PASSED' -> None`、`'' -> None`、`None -> None`。

**未知值仍判 invalid 实测**：构造 `status:"bogus"` 的机器结果，`result verify` 返回 `errors: ["invalid status", ...]`，`status: fail`，exit 2；构造 `acceptance[].status:"PASSED"`，返回 `errors: ["acceptance 1 has invalid status"]`，exit 2。**闸门未放宽**。

词表常量（`core.py:34-36` 及 58 行前的赋值）与改前集合成员逐一对照，**没有偷偷加值**：

- `REPORT_STATUSES = (PASS, FAIL, BLOCKED, FLAKY, EXPLORATORY_ONLY, READY-TO-MERGE, MERGED)` —— 即原 `evidence_verify` 局部 `valid_statuses`。
- `PRE_MERGE_REPORT_STATUSES = (PASS, READY-TO-MERGE)`；`POST_MERGE_REPORT_STATUSES = (PASS, READY-TO-MERGE, MERGED)`。
- `RESULT_STATUSES = (pass, fail, blocked, flaky)`；`ACCEPTANCE_STATUSES = (pass, fail, blocked, flaky, unverified)`。
- `RESULT_ROLE_ALIASES = {main: main-final, final: main-final}`。

## D. 六处校验点的改动（逐处）

1. `core.py` `evidence_verify` 局部 `valid_statuses` 已删除，`expected_roles` 直接跟随（现 `:408`），词表上移为模块常量 `REPORT_STATUSES`。
2. `core.py:457`：`if normalize_status(value.get("status"), REPORT_STATUSES) is None:` —— 走归一。
3. `core.py:1235`：`if normalize_status(value.get("status"), RESULT_STATUSES) is None:` —— 走归一。
4. `core.py:1248`：`if normalize_status(item.get("status"), ACCEPTANCE_STATUSES) is None:` —— 走归一。
5. `core.py:1705/1707`：`normalize_status(status, PRE_MERGE_REPORT_STATUSES) is None` 与 `normalize_status(status, POST_MERGE_REPORT_STATUSES) is None` —— phase 集合内容未变。
6. `reconcile.py:88`：`all(normalize_status(status, POST_MERGE_REPORT_STATUSES) is not None for status in statuses)`。

逐处确认：判定逻辑确实走归一函数；phase 语义与集合内容未变；无额外放宽（`MERGED` 仍只在 post-merge 集合内，pre-merge 仍不含）。

## E. `planning.py` 三处既有归一

完整 diff 已读。导入从 `from .core import RETAINED_EVIDENCE_NAMES` 扩展为多行（`ACCEPTANCE_STATUSES`、`POST_MERGE_REPORT_STATUSES`、`RESULT_STATUSES`、`RETAINED_EVIDENCE_NAMES`、`normalize_status`、`resolve_result_role`）。

- `_validate_finalization_report`（现 `:2095`）：`normalize_status(value.get("status"), POST_MERGE_REPORT_STATUSES) is not None`。
- `_validate_finalization_acceptance`：`normalize_status(item.get("status"), ACCEPTANCE_STATUSES) != "pass"`。
- `_validate_result`（现 `:2131`）：`role_ok = resolve_result_role(value.get("role")) == resolve_result_role(expected_role)` 且 `normalize_status(value.get("status"), RESULT_STATUSES) == "pass"`。

写死特例 `{expected_role, "main-final"}` 已被 `resolve_result_role` 等价替代（`final`/`main` 都折叠到 `main-final`）。

**无循环导入**：`python -c "import pipeline_tools.core, pipeline_tools.planning, pipeline_tools.reconcile"` → `imports OK`，exit 0。

## F. final role 映射

- `__main__.py:350`：`choices=("executor", "reviewer", "final")`，新增 `final`。
- `resolve_result_role('final') = 'main-final'`；`'main' -> 'main-final'`。
- `'executor' -> 'executor'`、`'reviewer' -> 'reviewer'`、`'bogus' -> 'bogus'`（未知值透传，随后与期望角色比较时仍会 mismatch，未放宽）。
- `verify_structured_result` 的 role 判定（`core.py:1233`）改为双端归一比较；`executor` 仍只匹配 `executor`，`reviewer` 仍只匹配 `reviewer`。

## G. 新测试核验

类归属（`grep -n`）：

- `tests/test_evidence.py`：`EvidenceTests`（`class` 于 `:32`）内含 `:617`、`:630`、`:637`、`:644` 四条契约测试，另有 `:656`、`:667` 两条防退化测试。
- `tests/test_cli.py`：`CLITests`（`:37`）内含 `:70` `test_result_verify_cli_accepts_final_role`、`:85` `test_result_verify_cli_accepts_reviewer_role`。
- `tests/test_acceptance_id_and_template_compliance.py`：`AcceptanceIdAndTemplateComplianceTests`（`:23`）内含 `:61`/`:70` `test_references_document_one_status_vocabulary`。

方法体均含实质断言（非空壳）：1) `evidence_verify(...) == []` 且 `gate_check` 不含 `status is invalid` / `not mergeable`；2) `verify_structured_result(...) == []`；3) 断言 `PASS`/`Pass` 归一；4) 遗留值归一；5) 文档含 `归一`/`pass_with_conditions`/`evidence_verify`/`verify_structured_result` 且模板 `status == "PASS"`。

**实跑 6 条契约测试**：`Ran 6 tests in 0.211s`，`OK`，exit 0。

**防退化测试有效**：`test_unknown_report_status_stays_invalid` 断言 `review-report.md status is invalid`；`test_unknown_result_status_stays_invalid` 断言 `'invalid status' in errors`。两者钉住「未知值仍 invalid」，有效。

**既有测试未被削弱**：`git diff 82d4827 HEAD -- tests/` 的删除行只有 1 行——`from pipeline_tools.core import evidence_freshness, evidence_verify, gate_check` 被改为加入 `verify_structured_result` 的版本（导入行替换）。**无任何既有断言被删除或放宽**。

**中途修正核验**：`grep -n "class StatusVocabularyTests" tests/` **无命中**，无残留类；4 条方法确在 `EvidenceTests` 内。

**缺陷（真实）**：`tests/test_acceptance_id_and_template_compliance.py` 第 61 行与第 70 行**重复定义了同一个方法名** `test_references_document_one_status_vocabulary`。Python 中后者覆盖前者，前一份成为死代码；`unittest` 只收集到 1 个（`-v | grep -c` = 1）。两次定义由本次提交同时引入（diff 中两段均为 `+`）。此为真实缺陷，建议删除其中一份（保留含 `assertIn("pass", ...)` 的较强者）。

## H. 「修复前红」独立复现

在系统 temp 树用 `git archive 82d4827 | tar -x` 得基线实现，覆盖 HEAD 的三个测试文件与 `references/acceptance-evidence.md`，跑 6 条：

- 结果：`Ran 6 tests in 0.312s`，`FAILED (failures=5)`，exit 1。
- 失败详情（摘录）：`['invalid status', 'acceptance 1 has invalid status'] != []`；`['executor-report.md status is invalid', 'review-report.md status is invalid', 'final-check.md status is invalid'] != []`。
- 第 6 条（文档）在把文档改动一并覆盖后**通过**，与执行者「文档测试不单独取红」的如实标注一致。

**5 条行为测试在基线实现下确实红**，具备区分力；第 6 条是文档/模板断言，不依赖实现，符合预期。

## I. 端到端验证

修复后（当前 HEAD）：

- `result verify .pipeline/evidence-retention-forward-gate/reviewer-result.json --role reviewer` → `status: pass`，`errors: []`，exit 0。
- `result verify .pipeline/gate-deletion-semantics/final-result.json --role final` → `status: pass`，`errors: []`，exit 0。

反例仍被拒（系统 temp 构造）：

- `status:"bogus"` → `errors: ["invalid status", ...]`，exit 2。
- `acceptance[].status:"PASSED"` → `errors: ["acceptance 1 has invalid status"]`，exit 2。

闸门未被放宽。修复前的红由 H 步复现（基线实现 + 新测试 failures=5），与执行者自述方向一致。

## J. 全量测试

`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests` → `Ran 294 tests in 204.618s`，`OK`，exit 0。基线 285，本次 294（+9 收集）。注意：因 G 步的重复方法，其中 1 个「新增」是重复定义（收集数仍 +9）。

## K. 三份历史产物哈希对照

| 文件 | 基线 sha256 | 本次实测 |
|---|---|---|
| `.pipeline/gate-deletion-semantics/final-result.json` | `c8e61ee06578c5db938253d9c149c5587c9f2b7b7326b84212b0b998eed249d7` | 一致 |
| `.pipeline/evidence-retention-forward-gate/reviewer-result.json` | `1f305f8ffbdc12ad50ac4e03a6de4142a473d97c98fc90a54bf24398227ccb15` | 一致 |
| `.pipeline/evidence-retention-forward-gate/review-report.md` | `354c3d8fc725c771c3d944b235fba6201408953f62cbd9bba0bc1017d8dcba5d` | 一致 |

三者全部匹配（见 I 步命令输出）。

## L. 文档改动

`git diff 82d4827 HEAD -- references/acceptance-evidence.md` 新增「状态词表与读取侧归��」章节，写清：markdown 侧大写 / JSON 侧小写各自规范；`normalize_status` 单点定义、大小写与 `-`/`_` 不敏感、未知值返回 `None`；`LEGACY_STATUS_ALIASES` 把 `pass_with_conditions` 归一到 `pass`；两侧读取入口（`evidence_verify`/`gate_check`/`reconcile` 与 `verify_structured_result`）；`result verify --role final` 映射到 `main-final`。**满足契约「一套共享归一表 + 两侧读取入口 + 遗留值映射」**。

`templates/pipeline-evidence.json` 未被改动（`git diff --name-only` 为空，`status` 仍为 `"PASS"`），理由成立（模板本已是大写规范）。

## M. 证据合规性

- 证据目录文件：`executor-report.md`（21431 字节）、`executor-result.json`（2014 字节）。
- `git ls-files .pipeline/status-vocabulary-unification/`：仅上述两个；**无 `.log`、无 `freshness.json`**。
- `executor-report.md` 含**恰好 1 个** ` ```pipeline-evidence ` 块（`grep -c '^```pipeline-evidence'` = 1），` ```json ` 计数 0；块在文件末尾，JSON 合法；`role: executor`、块内 `status: "PASS"`（大写）；`commands[]` 每条有 `command`/整数 `exit_code`/`evidence_ref`，两条非零（exit 1、exit 3）均显式声明 `expected_exit_code`。
- `executor-result.json` JSON 合法；`status: "pass"`（小写）；`identity.product_head = 92ef248...`、`head = 92ef248...`；`acceptance` 6 条、`status` 均小写 `pass`、`exit_code` 0、`evidence_refs: ["executor-report.md"]`；`unverified` 5 项。
- `result verify .pipeline/status-vocabulary-unification/executor-result.json --task-id ... --role executor` → `status: pass`，`errors: []`，exit 0。
- **执行者如实报告失败/未完成项**：报告列了「独立审查未做」「主代理终审未做」「未合并」「第 6 条文档测试未单独取红」「metrics 趋势未验」——如实。

**与实测不符之处**：`executor-report.md` 第十节称 gate 缺 6 件（`executor-report.md` / `review-report.md` / `final-check.md` / `executor-result.json` / `reviewer-result.json` / `final-result.json`），**实测只有 4 条 errors**（`missing review-report.md`、`missing final-check.md`、`missing reviewer-result.json`、`missing final-result.json`）——`executor-report.md` 与 `executor-result.json` 均存在。执行者在 gate errors 条数上多报 2 条。

## N. gate 自检

`gate pre-merge .pipeline/status-vocabulary-unification --task-id ... --branch ...` → `status: blocked`，exit 3，**errors 恰 4 条**：`missing review-report.md`、`missing final-check.md`、`missing reviewer-result.json`、`missing final-result.json`。符合「此刻只有 executor 一份」的预期。

## O. `task validate`

`task validate docs/tasks/status-vocabulary-unification.md` → `status: pass`，`errors: []`，exit 0。

## 6 条验收逐条判定

| # | 验收 ID | 独立结果 |
|---|---|---|
| 1 | acceptance-test-markdown-report-status-normalized | PASS |
| 2 | acceptance-test-machine-result-status-normalized | PASS |
| 3 | acceptance-test-result-verify-accepts-final-role | PASS |
| 4 | acceptance-test-legacy-status-values-normalized | PASS |
| 5 | acceptance-test-legacy-report-status-value-normalized | PASS |
| 6 | acceptance-test-status-vocabulary-documented | PASS |

## 与执行者自述不符之处

1. 重复定义测试方法 `test_references_document_one_status_vocabulary`（第 61、70 行），执行者未提及；「9 条新增」中 1 条实为重复定义。
2. `executor-report.md` 第十节称 gate 缺 6 件产物，实测 4 条 errors（多报 2 条）。

## 无法确定项

- `executor-result.json` 的 `identity.head` 填 `92ef248`（执行提交），而证据提交为 `0b5c8fb`；若约定要求 `head` 指向证据生成时的 HEAD，则应更接近 `0b5c8fb`。此为约定解释问题，不影响验收。

## 需主代理终审裁决项

- 重复测试方法是否要求执行者回修后合并（本审查判为 ACCEPT WITH CONDITIONS）。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "status-vocabulary-unification",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/status-vocabulary-unification",
  "branch": "status-vocabulary-unification",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_normalized_report_statuses tests.test_evidence.EvidenceTests.test_result_verify_accepts_normalized_result_statuses tests.test_cli.CLITests.test_result_verify_cli_accepts_final_role tests.test_evidence.EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions tests.test_evidence.EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_document_one_status_vocabulary",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/evidence-retention-forward-gate/reviewer-result.json --task-id evidence-retention-forward-gate --role reviewer",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/gate-deletion-semantics/final-result.json --task-id gate-deletion-semantics --role final",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify <tmp>/neg-result.json --task-id status-vocabulary-unification --role executor",
      "exit_code": 2,
      "expected_exit_code": 2,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/status-vocabulary-unification/executor-result.json --task-id status-vocabulary-unification --role executor",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "sha256sum .pipeline/gate-deletion-semantics/final-result.json .pipeline/evidence-retention-forward-gate/reviewer-result.json .pipeline/evidence-retention-forward-gate/review-report.md",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json task validate docs/tasks/status-vocabulary-unification.md",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/status-vocabulary-unification --task-id status-vocabulary-unification --branch status-vocabulary-unification",
      "exit_code": 3,
      "expected_exit_code": 3,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "git archive 82d4827 | tar -x -C <tmp> && cp <HEAD tests+references> <tmp> && python -m unittest <6 acceptance tests>",
      "exit_code": 1,
      "expected_exit_code": 1,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -c \"import pipeline_tools.core, pipeline_tools.planning, pipeline_tools.reconcile; print('imports OK')\"",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    }
  ],
  "assertions": [
    "the frozen task sheet sha256 is unchanged from 82d4827 (97e0c80b...)",
    "normalize_status ignores case and -/_ separators, applies LEGACY_STATUS_ALIASES, returns the canonical vocabulary spelling, and returns None for unknown values",
    "unknown values are still rejected end-to-end: status 'bogus' and acceptance status 'PASSED' both yield invalid-status errors with exit 2",
    "all six contract acceptance tests pass independently (Ran 6 tests, OK)",
    "all three historical evidence artifacts keep their exact baseline sha256 values",
    "the full suite is 294 tests, OK",
    "gate pre-merge reports exactly 4 errors: missing review-report.md, final-check.md, reviewer-result.json, final-result.json",
    "no circular import between core, planning and reconcile",
    "with the baseline implementation and the new tests, 5 of 6 acceptance tests fail (Ran 6 tests, FAILED failures=5)",
    "tests/test_acceptance_id_and_template_compliance.py defines test_references_document_one_status_vocabulary twice (lines 61 and 70), leaving one definition dead",
    "the executor report lists six missing gate artifacts but the gate reports four"
  ],
  "evidence_refs": [
    "review-report.md"
  ],
  "unverified": [
    "the 'main' alias of resolve_result_role on a real final-check chain (only static planning.py call-site evidence)",
    "cross-task metrics growth trend",
    "whether identity.head in executor-result.json should name the evidence commit rather than the execution commit"
  ],
  "verdict": "ACCEPT WITH CONDITIONS",
  "recommendation": "ready_for_final_check"
}
```