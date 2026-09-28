# 主代理终审报告：toolchain-freshness-fixes

## 任务身份

- task_id：`toolchain-freshness-fixes`
- worktree：`.worktrees/toolchain-freshness-fixes`（绝对路径 `D:\Projects\Skills\pipeline\.worktrees\toolchain-freshness-fixes`）
- branch：`toolchain-freshness-fixes`
- 角色：main-final
- round：1
- 基线：`fa485f4`（冻结任务单）
- 提交链：`6994f7b`（执行者：core.py 修复 + 4 条新测试 + 文档）、`b18faa4`（执行者证据）、`1b1aaad`（独立审查）
- 当前 HEAD：`1b1aaad1e88670ec4b328b49c1fca5df77c495f0`
- 环境：Windows / Git Bash，Python 3.12
- 本报告全部命令均由本轮独立实跑；未采信执行者或审查者的摘要。

---

## 一、任务 1：第 5 条验收测试落点偏差的裁定

### 1.1 独立核验证据

读契约原文 `docs/tasks/toolchain-freshness-fixes.md:167-168`：

```
"test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis",
"command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis"
```

读同一契约的 `allowed_paths`（`docs/tasks/toolchain-freshness-fixes.md:28-33`），恰好 4 个文件：

```
pipeline_tools/core.py
tests/test_evidence.py
references/acceptance-evidence.md
references/execution-and-review.md
```

`tests/test_acceptance_id_and_template_compliance.py` **不在**其中。

grep 全仓确认该方法的唯一实际落点：

```
tests/test_evidence.py:517:    def test_references_execution_and_review_documents_freshness_resolution_basis(self):
```

实跑两条命令（本轮独立执行）：

| 命令 | 结果 |
|---|---|
| 契约 `command_ref` 原文 | `AttributeError: type object 'AcceptanceIdAndTemplateComplianceTests' has no attribute '...'`，`Ran 1 test`，`FAILED (errors=1)`，exit 1 |
| 实际落点 `tests.test_evidence.EvidenceTests.<同名方法>` | `Ran 1 test ... OK`，exit 0 |

### 1.2 裁定

**接受现状（测试留在 `tests/test_evidence.py`），并记录为契约缺陷。**

理由：契约自相矛盾——它同时要求该测试存在，又禁止修改承载它的文件。执行者选择守 `allowed_paths`、把同名同断言的方法放进允许的 `tests/test_evidence.py`，是唯一能同时满足两条硬约束的做法；改 `allowed_paths` 或改冻结任务单都属于禁改动作。测试语义未削弱：方法名、断言、覆盖的文档不变量均未变。

根因在规划期：规划器生成的 `test_ref` 指向了同一契约 `allowed_paths` 之外的文件。

后续建议：另开 `derived` 任务，修正生成逻辑使 `acceptance_tests[].test_ref` 恒落在 `allowed_paths` 内，并加一条规划期一致性校验。

---

## 二、任务 2：gate 盲区记录

`grep -rn "test_ref\|command_ref" pipeline_tools/ scripts/` 全部命中：

```
pipeline_tools/contract.py:24:   ACCEPTANCE_FIELDS = ("id", "evidence_level", "test_ref", "command_ref")
pipeline_tools/contract.py:358:  for field in ("test_ref", "command_ref"):      # 仅字段存在性
pipeline_tools/planning.py:667:  for key in ("evidence_level", "test_ref", "command_ref"):  # 必填校验
pipeline_tools/planning.py:673:  for key in ("test_ref", "command_ref"):                 # 必填校验
pipeline_tools/planning.py:1647: lines.extend([... f"`{test.get('test_ref')}`" ...])   # 渲染进任务单
```

确认：只有字段存在性校验与任务单渲染，**没有任何代码把 `test_ref` / `command_ref` 与磁盘上测试的真实位置做比对**。因此任务 1 的偏差对全部机械闸门不可见。

裁定：登记为后续改进议题，另开任务处理。它与已知缺陷 E（`forbidden_paths`）是两个独立的闸门缺口，不应合并。

---

## 三、任务 3：`freshness.json` 处置

核验结果：

- `ls -la .pipeline/toolchain-freshness-fixes/`：只有 4 个文件（`executor-report.md`、`executor-result.json`、`review-report.md`、`reviewer-result.json`），**无 `freshness.json`**。
- `git log --all -- .pipeline/toolchain-freshness-fixes/freshness.json`：无输出。
- `git ls-files .pipeline/toolchain-freshness-fixes/`：4 个文件，无它。
- `git check-ignore -v`：rc=1，未被忽略。
- `find . -name freshness.json -not -path "./.git/*"`：无输出。
- 本轮再次实跑 freshness 之后，该文件**仍未出现**。

代码依据：`pipeline_tools/core.py:1425` 只在返回结果的 `artifacts` 字段里报告 `evidence_directory / "freshness.json"` 这个**路径字符串**，`evidence_freshness` 全程没有任何写文件动作。保留集契约（`references/acceptance-evidence.md`）的 7 个名字由 `core.py:26` 的 `RETAINED_EVIDENCE_NAMES = REPORT_NAMES + MACHINE_RESULT_NAMES + ("finalization.json",)` 单点定义，`freshness.json` 不在其中。

**决定：不删除，因为不存在可删之物。** 审查者报告中提到的残留无法复现；我也没有任何文件需要清理，故本轮未对证据目录做删除操作。

---

## 四、核心事实的独立复核

### 4.1 提交与边界

- `git log --oneline -6`：`1b1aaad` → `b18faa4` → `6994f7b` → `fa485f4`（基线）。
- `git diff fa485f4 HEAD --name-status`（全部改动，8 个）：

```
A  .pipeline/toolchain-freshness-fixes/executor-report.md
A  .pipeline/toolchain-freshness-fixes/executor-result.json
A  .pipeline/toolchain-freshness-fixes/review-report.md
A  .pipeline/toolchain-freshness-fixes/reviewer-result.json
M  pipeline_tools/core.py
M  references/acceptance-evidence.md
M  references/execution-and-review.md
M  tests/test_evidence.py
```

非证据改动恰好是 `allowed_paths` 的 4 个文件，无越界。

### 4.2 五条验收测试逐条实跑

前 4 条按契约 `command_ref` 合并实跑：`Ran 4 tests in 4.831s`，**OK**，exit 0。

| # | id | 落点 | 结果 |
|---|---|---|---|
| 1 | acceptance-test-acceptance-evidence-refs-resolve-from-evidence-directory | tests.test_evidence | exit 0 |
| 2 | acceptance-test-acceptance-evidence-refs-still-reject-absolute-and-traversal | tests.test_evidence | exit 0 |
| 3 | acceptance-test-freshness-metrics-commit-keeps-evidence-only | tests.test_evidence | exit 0 |
| 4 | acceptance-test-freshness-product-drift-still-blocks | tests.test_evidence | exit 0 |
| 5 | acceptance-test-freshness-docs-aligned | 契约原文 → exit 1（AttributeError）；实际落点 `tests.test_evidence.EvidenceTests....` → exit 0 | 落点偏差，见任务 1 |

### 4.3 全量测试

`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests`
→ **`Ran 279 tests in 203.732s`，OK**，进程 exit 0。与基线 279 一致。

### 4.4 任务单字节

`sha256sum docs/tasks/toolchain-freshness-fixes.md`
→ `8bcc46f11556b926222ff46fabe79d26ee8bdeccd79a78f9b76da67f18555584`，与冻结值一致，未变。

### 4.5 端到端 freshness（本轮核心）

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/toolchain-freshness-fixes --result .pipeline/toolchain-freshness-fixes/executor-result.json
```

返回：

- `status`: **pass**，`errors`: **[]**，exit 0
- `observed.product_head`: `6994f7ba20375e5c7bc8f5dc2da9ed0b308690a0`
- `observed.changed_paths`: 4 个证据目录文件
- `observed.evidence_only`: **true**

**`evidence artifact missing` 与 `product/test HEAD drifted` 两条都消失。**

### 4.6 产品漂移守卫未被放宽

`tests/test_evidence.py:82 test_freshness_blocks_product_drift_from_product_head` 包含在 4.2 的合并实跑中，**exit 0 通过**——证明豁免只扩展到了 metrics，产品/测试改动仍触发 `product/test HEAD drifted`。

### 4.7 两个缺陷的代码抽查（自己看）

- **缺陷 C**：`core.py:1412-1417` 对 `acceptance[].evidence_refs` 的缺失判定调用 `_evidence_file_exists(evidence_directory, reference)`，与 `commands[].evidence_ref` 同基准（`core.py:313`）。
- **缺陷 D**：`core.py:1390-1395` 的 `evidence_only` 判定为 `path == evidence_root or path.startswith(evidence_root + "/") or is_metrics_path(path)`，确实含 `is_metrics_path`（`layout.py:82`），与 `scope_check`（`core.py:286`）同口径。
- **`_validate_evidence_ref`（`core.py:293-302`）** 仍拒绝绝对路径（`Path.is_absolute()`、`^[A-Za-z]:/`、以 `/` 开头）与 `..` 穿越（`".." in normalized.split("/")`）——守卫未被削弱。

---

## 五、对执行与审查两阶段的确认

- 执行者（`6994f7b`/`b18faa4`）：守 `allowed_paths`，两个缺陷修复有对应新测试，报告与机器结果齐备。
- 审查者（`1b1aaad`）：结论 ACCEPT WITH CONDITIONS，其关键事实（越界检查、任务单哈希、四象限、端到端 freshness、全量 279）本轮抽查复核一致；其关于 `freshness.json` 残留的说法**无法复现**（见任务 3）。

本报告未引用任何已删除的原始日志；所有断言均出自本轮可复现命令或当前磁盘文件。

---

## 六、结论

**ACCEPT WITH CONDITIONS。** 产品改动正确、范围合规、全量绿、端到端 freshness 通过；唯一未决项是冻结契约自身的 `acceptance_tests[5].test_ref` ��界缺陷（及其对应的闸门盲区），需另开 `derived` 任务修正生成逻辑。是否合并由人类开发者决定。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "toolchain-freshness-fixes",
  "worktree": ".worktrees/toolchain-freshness-fixes",
  "branch": "toolchain-freshness-fixes",
  "role": "main-final",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal tests.test_evidence.EvidenceTests.test_freshness_allows_metrics_only_commit_after_product_head tests.test_evidence.EvidenceTests.test_freshness_blocks_product_drift_from_product_head",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis",
      "exit_code": 1,
      "expected_exit_code": 1,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest tests.test_evidence.EvidenceTests.test_references_execution_and_review_documents_freshness_resolution_basis",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/toolchain-freshness-fixes --result .pipeline/toolchain-freshness-fixes/executor-result.json",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "sha256sum docs/tasks/toolchain-freshness-fixes.md",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "final-check.md"
    }
  ],
  "assertions": [
    "non-evidence diff since fa485f4 is exactly the four allowed_paths files: pipeline_tools/core.py, tests/test_evidence.py, references/acceptance-evidence.md, references/execution-and-review.md",
    "frozen task sheet sha256 unchanged: 8bcc46f11556b926222ff46fabe79d26ee8bdeccd79a78f9b76da67f18555584",
    "acceptance tests 1-4 pass at the contract command_ref locations: Ran 4 tests, OK, exit 0",
    "acceptance test 5 at the contract command_ref fails with AttributeError and exit 1; the method exists only in tests/test_evidence.py and passes there with exit 0",
    "full suite: Ran 279 tests in 203.732s, OK, exit 0",
    "end-to-end freshness: status=pass, errors=[], evidence_only=true; both 'evidence artifact missing' and 'product/test HEAD drifted' are absent",
    "product drift guard test_freshness_blocks_product_drift_from_product_head still passes, so the metrics exemption did not widen the product-drift gate",
    "defect C fixed: acceptance[].evidence_refs resolves via _evidence_file_exists(evidence_directory, ref), same basis as commands[].evidence_ref",
    "defect D fixed: evidence_only includes is_metrics_path(path), matching scope_check",
    "_validate_evidence_ref still rejects absolute paths and '..' traversal",
    "no freshness.json exists in the evidence directory, in git history, or anywhere in the worktree; freshness does not write it",
    "pre-merge gate reports exactly the two missing final artifacts before this round (missing final-check.md, missing final-result.json)"
  ],
  "evidence_refs": [
    "final-check.md",
    "executor-report.md",
    "review-report.md",
    "executor-result.json",
    "reviewer-result.json",
    "final-result.json"
  ],
  "unverified": [
    "the reviewer's pre-fix red reproduction via git archive fa485f4 was not independently re-run this round; accepted only as reviewer-reported",
    "the reviewer's freshness run that reportedly wrote freshness.json could not be reproduced",
    "the exact planning.py branch that emitted the out-of-scope test_ref was located by call site only, not traced to its emitting condition"
  ]
}
```