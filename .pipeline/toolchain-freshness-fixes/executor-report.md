# 执行者报告：toolchain-freshness-fixes

## 任务身份

- task_id：`toolchain-freshness-fixes`
- worktree：`.worktrees/toolchain-freshness-fixes`（绝对路径 `D:\Projects\Skills\pipeline\.worktrees\toolchain-freshness-fixes`）
- branch：`toolchain-freshness-fixes`（由主工作树 `fa485f4` 创建）
- round：1
- baseline head：`fa485f489f518686da59211b641e26818cbcf481`
- 执行提交（product_head）：`6994f7ba20375e5c7bc8f5dc2da9ed0b308690a0`
- 证据提交：本次证据提交（见末尾 `git show --stat`），product_head 为其祖先

## 改动摘要

两个缺陷都在 `pipeline_tools/core.py` 的 `evidence_freshness` 内修复；4 条测试落在 `tests/test_evidence.py`；两份 reference 文档补齐解析基准与 metrics 豁免说明。改动严格落在任务单 `allowed_paths` 的 4 个文件内。

### 缺陷 C：`acceptance[].evidence_refs` 解析基准不一致

文件：`pipeline_tools/core.py`

改前（原 `core.py:1401-1407`）：

```python
    missing = []
    for reference in evidence_refs:
        candidate = root / reference.replace("\\", "/")
        if not candidate.is_file():
            missing.append(reference)
    if missing:
        errors.append("evidence artifact missing")
```

改后（现 `core.py:1401-1410`）：

```python
    # acceptance[].evidence_refs use the same basis as commands[].evidence_ref:
    # bare names resolve against the task evidence directory, while explicit
    # .pipeline/... references still resolve from the project root.
    missing = [
        reference
        for reference in evidence_refs
        if not _evidence_file_exists(evidence_directory, reference)
    ]
    if missing:
        errors.append("evidence artifact missing")
```

复用了既有的 `_evidence_file_exists`（`core.py:313-325`），其 `.pipeline/` 前缀分支保证以 `.pipeline/demo/test.log` 形式书写的既有引用仍从项目根解析，因此 `tests/test_evidence.py` 里既有的多条用例不被打破。绝对路径与 `..` 穿越引用由 `_validate_evidence_ref`（`core.py:293-302`）拒绝，返回 `False` → 仍报缺失。

### 缺陷 D：`evidence_only` 不豁免 `.pipeline/metrics/`

文件：`pipeline_tools/core.py`

改前（原 `core.py:1386-1388`）：

```python
                evidence_only = bool(evidence_root) and all(
                    path == evidence_root or path.startswith(evidence_root + "/") for path in changed_paths
                )
```

改后（现 `core.py:1386-1397`）：

```python
                # Metrics events are workflow metadata that may be committed to the
                # host project (see references/metrics-contract.md). scope_check
                # already exempts them; evidence_only must use the same basis or
                # every task that ran pipeline-tools flips to a false product drift.
                evidence_only = bool(evidence_root) and all(
                    path == evidence_root
                    or path.startswith(evidence_root + "/")
                    or is_metrics_path(path)
                    for path in changed_paths
                )
```

`is_metrics_path` 已在模块顶部从 `.layout` 导入（`core.py:17`），`scope_check` 亦使用同一判据（`core.py:286`），口径由此对齐。证据目录之外的产品或测试改动仍使 `evidence_only` 为假 → 仍报 `product/test HEAD drifted`（第 5 条测试守住）。

### 文档对齐

- `references/acceptance-evidence.md`：新增「证据引用解析基准」与「evidence_only 与 `.pipeline/metrics/`」两节。
- `references/execution-and-review.md`：在「执行期 goal 哈希稳定性」的执行检查点列表新增两条，写明 refs 解析基准与 metrics 豁免。

## 4 条新测试（TDD 红→绿）

全部位于 `tests/test_evidence.py`，类 `EvidenceTests`。

> **范围偏差（需裁决）**：任务单 `acceptance_tests[4]` 的 `test_ref` 指向 `tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis`，但该文件**不在** `allowed_paths`（只有 `pipeline_tools/core.py`、`tests/test_evidence.py`、两个 `references/`）。为避免改 `allowed_paths` 之外的文件，我把该测试放进 `tests/test_evidence.py` 的 `EvidenceTests` 类，方法名与断言不变。任务单未修改。

| 测试方法 | 断言什么 | 修复前结果 |
|---|---|---|
| `test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory` | 临时仓库里 `executor-result.json` 的 `acceptance[].evidence_refs` 写裸名 `test.log`，文件只在 `.pipeline/demo/` 下；断言 `errors` 不含 `evidence artifact missing`，且 `status == pass` | **FAIL**：`'evidence artifact missing' unexpectedly found in ['evidence artifact missing']` |
| `test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal` | 同一入口传绝对路径与 `../outside.log`；断言仍报 `evidence artifact missing` 且 `status == blocked`（防修复过宽） | **ok**（守卫，应已通过） |
| `test_freshness_allows_metrics_only_commit_after_product_head` | `product_head..HEAD` 只新增 `.pipeline/metrics/<id>.json`；断言 `errors` 不含 `product/test HEAD drifted`，且 `observed` 中 `evidence_only` 为 `True` | **FAIL**：`'product/test HEAD drifted' unexpectedly found in [...]`，`evidence_only: False` |
| `test_references_execution_and_review_documents_freshness_resolution_basis` | 断言 `references/acceptance-evidence.md` 与 `references/execution-and-review.md` 均含 `acceptance[].evidence_refs`、`证据目录`、`.pipeline/metrics/`、`evidence_only` | **FAIL**：`'acceptance[].evidence_refs' not found` |

修复前命令与结果（4 条一起跑）：

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest -v \
  tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory \
  tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal \
  tests.test_evidence.EvidenceTests.test_freshness_allows_metrics_only_commit_after_product_head \
  tests.test_evidence.EvidenceTests.test_references_execution_and_review_documents_freshness_resolution_basis
```

结果：`Ran 4 tests in 3.533s` / `FAILED (failures=3)`（3 条目标测试红，守卫测试 ok）。

修复后同一批 4 条全绿（包含在下面的针对性全跑中）。

## 第 5 条既有测试

`tests/test_evidence.py:82 EvidenceTests.test_freshness_blocks_product_drift_from_product_head`（`evidence_only` 修复前已存在）仍通过：针对性全跑 `Ran 50 tests ... OK` 中该用例为 `ok`。它守住「产品代码漂移仍报错」这一核心闸门。

## 测试结果

### 针对性（修复后）

```
cd D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence tests.test_acceptance_id_and_template_compliance
```

结果：`Ran 50 tests in 7.995s` / `OK`

### 全量（门禁）

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests
```

结果：`Ran 279 tests in 209.124s` / `OK`

基线为主工作树当前值 **275**；本次新增 4 条 → 279，符合预期。

## 端到端 `freshness` 验证

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/toolchain-freshness-fixes --result .pipeline/toolchain-freshness-fixes/executor-result.json
```

实际输出（原样，一行 JSON）：

```json
{"artifacts": [".pipeline\\toolchain-freshness-fixes\\freshness.json"], "blockers": [], "command": "evidence.freshness", "errors": [], "next_actions": [], "observed": [{"fact": "head", "value": "6994f7ba20375e5c7bc8f5dc2da9ed0b308690a0"}, {"fact": "implement_plan_recorded", "value": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f"}, {"fact": "implement_plan_observed", "value": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f"}, {"fact": "product_head", "value": "6994f7ba20375e5c7bc8f5dc2da9ed0b308690a0"}, {"fact": "changed_paths", "value": []}, {"fact": "evidence_only", "value": true}], "result_sha256": "e428dd733ae489f7a59fa2e144437d35983a2c05d675d74fc18c7c55695267e3", "schema": 1, "status": "pass", "unverified": []}
```

关键观察：

- `errors` 为 `[]` —— **`evidence artifact missing` 已消失**，这正是缺陷 C 的修复目标（报告与 `executor-result.json` 里的 `acceptance[].evidence_refs` 均写裸名 `executor-report.md`，现在从证据目录解析成功）。
- `product/test HEAD drifted` **未出现**，`evidence_only` 为 `true`，`changed_paths` 为 `[]`（本次 freshness 运行时 HEAD 即 product_head，无额外提交）。
- `implement_plan_recorded` 与 `implement_plan_observed` 相等（均为 `goal.md` 的契约哈希），无需求漂移。
- `status` 为 `pass`。

该命令顺带写出 `.pipeline/toolchain-freshness-fixes/freshness.json`（每次运行的原始产物，不在 7 个保留文件名内，最终化时会被清理）。它未进入任何提交；本报告已逐字记录其 stdout，故删除该可重生成的原始文件以保持工作区干净。

## 未完成项 / 未验证项

- 独立审查（`review-report.md` / `reviewer-result.json`）未做——由审查子代理在其他轮次完成。
- 主代理终审（`final-check.md` / `final-result.json`）未做。
- 未 push、未合并、未删除 worktree、未 amend。
- 未修改冻结任务单；`docs/tasks/toolchain-freshness-fixes.md` 的 sha256 前后一致（见下）。
- 第 4 条验收测试的落点与任务单 `test_ref` 不一致（见上方「范围偏差」），需主代理裁决。
- `.pipeline/metrics/` 下有两个由工具自动采集产生的未跟踪事件文件；按契约 `metrics` 应入库，但任务单 `allowed_paths` 不含它们，故本提交未纳入（保留在工作区）。
</content>
## 机器证据

```pipeline-evidence
{
  "schema": 1,
  "task_id": "toolchain-freshness-fixes",
  "worktree": ".worktrees/toolchain-freshness-fixes",
  "branch": "toolchain-freshness-fixes",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_evidence tests.test_acceptance_id_and_template_compliance",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m pipeline_tools --format json freshness . .pipeline/toolchain-freshness-fixes --result .pipeline/toolchain-freshness-fixes/executor-result.json",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "executor-report.md"
    }
  ],
  "assertions": [
    "targeted suite passed: Ran 50 tests, OK",
    "full suite passed: Ran 279 tests, OK",
    "acceptance[].evidence_refs written as a bare filename resolve from the evidence directory"
  ],
  "evidence_refs": [
    "executor-report.md"
  ],
  "unverified": [
    "independent review not performed by this executor round",
    "main-agent final check not performed",
    "merge not performed"
  ]
}
```