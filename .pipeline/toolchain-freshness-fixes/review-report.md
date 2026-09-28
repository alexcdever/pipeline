# 审查报告：toolchain-freshness-fixes（独立复核）

## 审查身份

- task_id：`toolchain-freshness-fixes`
- worktree：`.worktrees/toolchain-freshness-fixes`（绝对路径 `D:\Projects\Skills\pipeline\.worktrees\toolchain-freshness-fixes`）
- branch：`toolchain-freshness-fixes`（`git worktree list --porcelain` 核对一致）
- 角色：reviewer
- round：1
- 基线：`fa485f4`（冻结任务单）
- 被审执行提交：`6994f7b`（product）、`b18faa4`（证据）
- 当前 HEAD：`b18faa4843027e8e0804a62f4664cb2c34895b90`
- 环境：Python 3.12.10，Windows / Git Bash
- 本报告所有命令均本轮独立实跑，未采信执行者自述输出。

---

## A. 提交与边界

```
git log --oneline -5
b18faa4 chore(evidence): record executor report and machine result
6994f7b fix(core): resolve acceptance evidence refs from evidence directory
fa485f4 Freeze generated task toolchain-freshness-fixes
437e0e2 final(record): accept derived record with adjudicated freshness gap
ba5e8bb review(record): independent verification of gate-deletion-semantics derived record
```

`git diff fa485f4 HEAD --name-status`（全量改动）：

```
A   .pipeline/toolchain-freshness-fixes/executor-report.md
A   .pipeline/toolchain-freshness-fixes/executor-result.json
M   pipeline_tools/core.py
M   references/acceptance-evidence.md
M   references/execution-and-review.md
M   tests/test_evidence.py
```

**边界结论：未越界。** 非证据改动恰好是 `allowed_paths` 的 4 个文件
（`pipeline_tools/core.py`、`tests/test_evidence.py`、`references/acceptance-evidence.md`、
`references/execution-and-review.md`），其余 2 条是证据目录文件。

`git status --short --untracked-files=no` 为空（无已跟踪文件未提交改动）。

`.pipeline/metrics/` 删除检查：

```
git log --diff-filter=D --name-only --oneline fa485f4..HEAD -- .pipeline/metrics/
(无输出)
git log --oneline fa485f4..HEAD -- .pipeline/metrics/
(无输出)
```

**结论：本任务范围提交内没有删除、也没有改动任何 `.pipeline/metrics/` 文件（0 条）。**
工作区有 3 个未跟踪的 metrics 事件（工具自动采集产物），均保留未删。

`git show --stat 6994f7b`：`core.py +22/-6`、`acceptance-evidence.md +10`、
`execution-and-review.md +2`、`test_evidence.py +81`，共 4 文件 109 插入 6 删除。
`git show --stat b18faa4`：仅 2 个证据文件 258 插入。

---

## B. 任务单字节未变

```
sha256sum docs/tasks/toolchain-freshness-fixes.md
8bcc46f11556b926222ff46fabe79d26ee8bdeccd79a78f9b76da67f18555584
git show fa485f4:docs/tasks/toolchain-freshness-fixes.md | sha256sum
8bcc46f11556b926222ff46fabe79d26ee8bdeccd79a78f9b76da67f18555584
```

**一致**，与执行者报的值相同。冻结任务单未被改动。

---

## C. 两个缺陷的实际改动（读源码独立核验）

### C1 缺陷 C：`acceptance[].evidence_refs` 解析基准

改后 `pipeline_tools/core.py:1408-1417`：

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

改前（`git show 6994f7b` 的 diff，删除侧）：

```python
    missing = []
    for reference in evidence_refs:
        candidate = root / reference.replace("\\", "/")
        if not candidate.is_file():
            missing.append(reference)
```

**核验成立**：改前按仓库根 `root / ref` 解析，改后按证据目录解析。

`_evidence_file_exists`（`core.py:313-325`）**确实**有 `.pipeline/` 前缀分支：

```python
    base = project_root if normalized == ".pipeline" or normalized.startswith(".pipeline/") else evidence_directory
    candidate = (base / normalized).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return False
    return candidate.is_file()
```

`_validate_evidence_ref`（`core.py:293-302`）**仍**拒绝绝对路径与 `..` 穿越：

```python
    return not (
        Path(normalized).is_absolute()
        or bool(re.match(r"^[A-Za-z]:/", normalized))
        or normalized.startswith("/")
        or ".." in normalized.split("/")
    )
```

`_evidence_file_exists` 首行即调用它，非法引用直接返回 `False` → 仍报缺失。**安全检查未被削弱。**

### C2 缺陷 D：`evidence_only` 豁免 metrics

改后 `pipeline_tools/core.py:1390-1395`：

```python
                evidence_only = bool(evidence_root) and all(
                    path == evidence_root
                    or path.startswith(evidence_root + "/")
                    or is_metrics_path(path)
                    for path in changed_paths
                )
```

`is_metrics_path` 定义在 `pipeline_tools/layout.py:82-90`，命中 `.pipeline/metrics` 或 `.pipeline/metrics/`；
`scope_check`（`core.py:286`）用的是同一函数：

```python
        if (is_metrics_path(normalized) or is_progress_log_path(normalized)) and not forbidden_match:
            continue
```

**口径一致**（同一函数、同一模块导入）。

---

## D. `evidence_only` 四象限核验（独立最小复现，落在系统 temp）

用真实 `evidence_freshness` 在临时 git 仓库中构造四个象限（脚本写在 `/tmp/quad_probe.py`，
仓库内不落任何文件）：

```
Q1 evidence-dir-only       evidence_only=[True]  status=pass     errors=[]
Q2 metrics-only            evidence_only=[True]  status=pass     errors=[]
Q3 product-code            evidence_only=[False] status=blocked  errors=['product/test HEAD drifted']
Q4 other-task-dir          evidence_only=[False] status=blocked  errors=['product/test HEAD drifted']
```

| 象限 | 改动内容 | 期望 | 实测 | 结论 |
|---|---|---|---|---|
| 证据目录内 | `.pipeline/demo/*` | `true` | `true` / pass | 通过 |
| metrics | `.pipeline/metrics/event-1.json` | `true` | `true` / pass | **新增豁免生效** |
| 产品代码 | `src/app.py` | `false` | `false` / blocked | **闸门未放宽** |
| 其它任务目录 | `.pipeline/other/test.log` | `false` | `false` / blocked | **闸门未放宽** |

**结论：`evidence_only` 语义精确，豁免只覆盖 `.pipeline/metrics/`，未泛化到整个 `.pipeline/`。**

---

## E. 4 条新测试（含「修复前确实红」的独立验证）

方法位置（`tests/test_evidence.py`，类 `EvidenceTests`）：

- `:465 test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory`
- `:478 test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal`
- `:494 test_freshness_allows_metrics_only_commit_after_product_head`
- `:517 test_references_execution_and_review_documents_freshness_resolution_basis`
- `:82  test_freshness_blocks_product_drift_from_product_head`（既有，闸门守卫）

关键断言摘录（非空壳，均为真实 `evidence_freshness` 调用 + 具体字段断言）：

- `:475` `assertNotIn('evidence artifact missing', value['errors'])`、`:476` `assertEqual(value['status'], 'pass')`
- `:491` `assertIn('evidence artifact missing', ...)`、`:492` `assertEqual(value['status'], 'blocked')`（防修复过宽）
- `:511` `assertNotIn('product/test HEAD drifted', ...)`、`:512-515` 断言 `observed` 中 `evidence_only` 为真
- `:522-526` 断言两份 reference 文本均含 `acceptance[].evidence_refs`、`证据目录`、`.pipeline/metrics/`、`evidence_only`
- `:96-97`（既有）产品漂移 → `status == 'blocked'` 且 `errors` 含 `product/test HEAD drifted`

### 本轮实跑（当前 HEAD，5 条一起）

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest -v \
  tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory \
  tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal \
  tests.test_evidence.EvidenceTests.test_freshness_allows_metrics_only_commit_after_product_head \
  tests.test_evidence.EvidenceTests.test_references_execution_and_review_documents_freshness_resolution_basis \
  tests.test_evidence.EvidenceTests.test_freshness_blocks_product_drift_from_product_head
```

结果：`Ran 5 tests in 4.786s` / `OK` / `EXIT=0`（5 条全 ok）。

### 「修复前确实红」的独立验证（只读，不落仓库）

用 `git archive fa485f4 | tar -x -C <系统 temp>` 导出基线，再把**当前的** `tests/test_evidence.py`
覆盖进去（测试新、实现旧），在 temp 中实跑：

```
TMP=/tmp/tff-pre-fix-1065
test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory ... FAIL
test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal ... ok
test_freshness_allows_metrics_only_commit_after_product_head ... FAIL
test_references_execution_and_review_documents_freshness_resolution_basis ... FAIL
test_freshness_blocks_product_drift_from_product_head ... ok
Ran 5 tests in 4.707s
FAILED (failures=3)
EXIT=1
```

失败原文（节选）：

- C：`'evidence artifact missing' unexpectedly found in ['evidence artifact missing']`，
  `changed_paths` 含 `.pipeline/demo/test.log` 而 `evidence_only=True` —— 证明缺失只源于 refs 解析基准。
- D：`'product/test HEAD drifted' unexpectedly found in [...]`，`evidence_only: False`。
- 文档测试：`'acceptance[].evidence_refs' not found`。

**结论：3 条目标测试在修复前确实红，且失败原因与缺陷 C/D 一一对应，非空壳、非事后编造；
守卫测试（拒绝绝对/穿越、产品漂移）在修复前即为绿，未被削弱。执行者自述的红绿分布与本轮独立复现完全一致。**

---

## F. 5 条 acceptance 逐条判定

| # | acceptance id | 契约 `command_ref` | 本轮实跑 | exit | 判定 |
|---|---|---|---|---|---|
| 1 | acceptance-test-acceptance-evidence-refs-resolve-from-evidence-directory | `tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory` | 同左，实跑 | 0 | PASS |
| 2 | acceptance-test-acceptance-evidence-refs-still-reject-absolute-and-traversal | `...test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal` | 同左，实跑 | 0 | PASS |
| 3 | acceptance-test-freshness-metrics-commit-keeps-evidence-only | `...test_freshness_allows_metrics_only_commit_after_product_head` | 同左，实跑 | 0 | PASS |
| 4 | acceptance-test-freshness-product-drift-still-blocks | `...test_freshness_blocks_product_drift_from_product_head` | 同左，实跑 | 0 | PASS |
| 5 | acceptance-test-freshness-docs-aligned | **`tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis`** | 契约命令**不存在**（见下）；按实际落点 `tests.test_evidence.EvidenceTests.test_references_execution_and_review_documents_freshness_resolution_basis` 实跑 | 契约命令=1，实际落点=0 | PASS（落点偏差，见 G） |

### 第 5 条落点偏差的实测证据

契约 `command_ref` 原样执行：

```
python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis
AttributeError: type object 'AcceptanceIdAndTemplateComplianceTests' has no attribute
'test_references_execution_and_review_documents_freshness_resolution_basis'
Ran 1 test in 0.000s
FAILED (errors=1)
EXIT=1
```

且该文件**在基线与当前 HEAD 都不含**该方法：

```
grep -n 'test_references_execution_and_review_documents_freshness_resolution_basis' tests/test_acceptance_id_and_template_compliance.py
(无匹配，rc=1)
grep -rn 'test_references_execution_and_review_documents_freshness_resolution_basis' tests/
tests/test_evidence.py:517
```

按实际落点执行：

```
python -m unittest tests.test_evidence.EvidenceTests.test_references_execution_and_review_documents_freshness_resolution_basis
EXIT=0（包含在 5 条批量 OK 中）
```

**与我读到的契约 `command_ref` 不一致 —— 契约那一条不可执行。**

---

## G. 范围偏差的独立评估

### G1 契约原文

- `acceptance_tests[4].test_ref`（任务单 :167）：
  `tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis`
- `acceptance_tests[4].command_ref`（:168）：同文件同方法
- `allowed_paths`（:28-33）与 `resources`（:47-52）**都不含** `tests/test_acceptance_id_and_template_compliance.py`，
  只有 `tests/test_evidence.py`。

### G2 实际位置

`grep -rn` 全 `tests/` 只有一个命中：`tests/test_evidence.py:517`，类 `EvidenceTests`。
`tests/test_acceptance_id_and_template_compliance.py` 里没有该方法（基线与 HEAD 均无）。

### G3 评估结论

1. **执行者守 `allowed_paths` 是对的。** 契约的 `allowed_paths` 是精确 4 文件白名单，
   `tests/test_acceptance_id_and_template_compliance.py` 不在其中；若为满足 `test_ref` 去改该文件，
   就构成越界，会被 `scope_check` / 机械 gate 拦下。两难之下选择「不改白名单外文件、
   把测试落到白名单内的 `tests/test_evidence.py`、保持方法名与断言不变、并主动上报偏差」
   是正确的工程取舍。
2. **gate 不会机械拦下这个偏差。** 我核验了 `gate_check`（`core.py:1544-1617`）与
   `evidence_verify`（`core.py:359-...`）：二者只校验报告的
   `schema/task_id/worktree/branch/role/round/status/commands/assertions/evidence_refs/unverified`、
   `commands[].exit_code`、以及三份 `*-result.json` 的存在与可解析。
   `grep -rn "test_ref\|command_ref" pipeline_tools/ scripts/` 的命中只有
   `contract.py:24/358`（字段存在性校验）与 `planning.py:667/673/1647`（任务单渲染）——
   **没有任何代码把 `test_ref` / `command_ref` 与磁盘上测试的真实位置做比对。**
   所以该偏差对 gate 不可见，既不会被拦，也不会被自动发现；必须靠人工/审查裁决。
3. **这是契约缺陷，不是执行偏差。** 根因是规划期生成的 `test_ref` 指向了 `allowed_paths`
   之外的文件，契约内部自相矛盾（`acceptance_tests[4]` 要求一个白名单外的落点）。
   执行者是契约缺陷的承受方而非制造方。
4. **建议处理**：
   - 接受现状（本轮结论），把测试留在 `tests/test_evidence.py`；
   - 另开 `derived` 任务修正契约生成逻辑，使 `acceptance_tests[].test_ref` 永远落在
     `allowed_paths` 内（或在规划期就把该文件加入 `resources`/`allowed_paths`）；
   - 不建议为此修改本已冻结的任务单。

---

## H. 端到端 freshness（独立复跑）

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json \
  freshness . .pipeline/toolchain-freshness-fixes \
  --result .pipeline/toolchain-freshness-fixes/executor-result.json
```

本轮实际输出（一行 JSON，节选观察项）：

```json
{"artifacts":[".pipeline\\toolchain-freshness-fixes\\freshness.json"],
 "blockers":[],"command":"evidence.freshness","errors":[],"next_actions":[],
 "observed":[{"fact":"head","value":"b18faa4843027e8e0804a62f4664cb2c34895b90"},
  {"fact":"implement_plan_recorded","value":"9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f"},
  {"fact":"implement_plan_observed","value":"9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f"},
  {"fact":"product_head","value":"6994f7ba20375e5c7bc8f5dc2da9ed0b308690a0"},
  {"fact":"changed_paths","value":[".pipeline/toolchain-freshness-fixes/executor-report.md",
                                  ".pipeline/toolchain-freshness-fixes/executor-result.json"]},
  {"fact":"evidence_only","value":true}],
 "status":"pass","unverified":[]}
EXIT=0
```

关键结论（独立复跑，非抄执行者）：

- `errors` 为 `[]` —— **`evidence artifact missing` 已消失**（缺陷 C 修复目标达成）。
- **`product/test HEAD drifted` 未出现**；`evidence_only` 为 `true`。
- 本次 `changed_paths` 非空（`b18faa4` 的证据提交），仍判 `evidence_only=true` —— 说明
  「product_head 之后的证据提交」这条主路径也真实可用，比执行者那次
  `changed_paths=[]` 的运行更强。
- `implement_plan_recorded == implement_plan_observed`（`9abb196a...`），无需求漂移。
- `status=pass`、`unverified=[]`。

> 该命令会写出 `.pipeline/toolchain-freshness-fixes/freshness.json`（可再生成的原始产物，
> 不属于 7 个保留名）。本次审查未删除该文件、也未删除任何 metrics 文件。

---

## I. 证据文件合规性

`.pipeline/toolchain-freshness-fixes/` 内容：

```
executor-report.md     11501 B
executor-result.json    1322 B
（审查后新增 review-report.md / reviewer-result.json）
```

`executor-report.md`：

- `grep -c '^```pipeline-evidence'` = **1**（恰好一个，位置在文件末尾 :168-210）。
- 块内 JSON 合法；字段齐全：`schema=1`、`task_id=toolchain-freshness-fixes`、
  `worktree=.worktrees/toolchain-freshness-fixes`、`branch=toolchain-freshness-fixes`、
  `role=executor`、`round=1`、`status=PASS`、`commands`（3 条）、`assertions`（3 条）、
  `evidence_refs=["executor-report.md"]`、`unverified`（3 条）。
- `commands[]` 3 条均有非空 `command`、整数 `exit_code`、`evidence_ref`；
  **无非零 exit_code**（全 0）。
- `evidence_refs` 用裸文件名 `executor-report.md`，该文件真实存在于证据目录。
- 诚实性：报告如实列出 4 条未完成/未验证项（无独立审查、无终审、未 push/merge、
  第 4 条落点偏差待裁决、metrics 未入库），**未把失败或未完成项包装成通过**。
  与上一轮被点名的「漏报 freshness 失败」相比，本轮报告完整。

`executor-result.json`：JSON 合法；`identity` 含 `product_head` 与 `head`
（均 `6994f7b...`）；`acceptance` 5 条全部 `status=pass`、`exit_code=0`、
`evidence_refs=["executor-report.md"]`；`unverified` 3 条。

`result verify`（本轮实跑）：

```
python -m pipeline_tools result verify --task-id toolchain-freshness-fixes \
  --role executor .pipeline/toolchain-freshness-fixes/executor-result.json
PASS  EXIT=0
```

---

## J. gate 自检（executor 单份时）

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json \
  gate pre-merge .pipeline/toolchain-freshness-fixes --task-id toolchain-freshness-fixes
```

```json
{"command":"gate.pre-merge",
 "errors":["missing review-report.md","missing final-check.md",
           "missing reviewer-result.json","missing final-result.json"],
 "exit_code":3,"status":"blocked","task_id":"toolchain-freshness-fixes"}
EXIT=3
```

**与预期一致**：blocked，errors 恰为缺 review/final 的 4 条。执行者在其报告「未完成项」中
如实声明了未做独立审查与终审，**与其自述一致**。

---

## K. 与执行者自述的差异

| 项 | 执行者自述 | 本轮独立结果 | 是否相符 |
|---|---|---|---|
| 全量测试 | `Ran 279 tests in 209.124s / OK` | `Ran 279 tests in 204.875s / OK` | 相符（数量与结果一致，耗时略异属正常） |
| 修复前红绿 | 4 条中 3 红 1 绿 | 独立复现 3 红 1 绿（守卫绿） | 相符 |
| 端到端 freshness | `errors=[]`、`evidence_only=true`、`status=pass` | 同（`changed_paths` 非空仍 pass） | 相符 |
| 任务单哈希 | `8bcc46f1...` | `8bcc46f1...` | 相符 |
| 边界 | 改动限于 allowed_paths 4 文件 | 确认未越界 | 相符 |
| 范围偏差 | 主动上报第 5 条落点偏差 | 确认为契约缺陷，执行者处置正确 | 相符，且其上报属实 |
| metrics | 未提交、保留工作区 | 确认 0 删除 | 相符 |

**未发现与执行者自述不符之处。**

---

## 结论

- 缺陷 C、D 的修复经源码阅读、四象限最小复现、端到端 freshness 三重独立核验，**正确且必要**；
  未放宽任何既有闸门（产品漂移、绝对路径/穿越引用仍被拒绝）。
- 5 条验收测试全部通过；第 5 条的契约 `command_ref` 不可执行，属**契约缺陷**，
  执行者在 `allowed_paths` 约束下的落点处理**正确**，gate 对此偏差**无机械拦截能力**。
- 执行者证据合规、如实报告未完成项。
- 审查判定：**ACCEPT WITH CONDITIONS**（条件：另开 `derived` 任务修正
  `acceptance_tests[].test_ref` 与 `allowed_paths` 的自相矛盾）。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "toolchain-freshness-fixes",
  "worktree": ".worktrees/toolchain-freshness-fixes",
  "branch": "toolchain-freshness-fixes",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal tests.test_evidence.EvidenceTests.test_freshness_allows_metrics_only_commit_after_product_head tests.test_evidence.EvidenceTests.test_references_execution_and_review_documents_freshness_resolution_basis tests.test_evidence.EvidenceTests.test_freshness_blocks_product_drift_from_product_head",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m pipeline_tools --format json freshness . .pipeline/toolchain-freshness-fixes --result .pipeline/toolchain-freshness-fixes/executor-result.json",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis",
      "exit_code": 1,
      "expected_exit_code": 1,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m pipeline_tools result verify --task-id toolchain-freshness-fixes --role executor .pipeline/toolchain-freshness-fixes/executor-result.json",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/toolchain-freshness-fixes",
      "evidence_ref": "review-report.md"
    }
  ],
  "assertions": [
    "non-evidence diff is exactly the four allowed_paths files; no out-of-scope file touched",
    "zero .pipeline/metrics files deleted or modified inside the task range",
    "frozen task sheet sha256 unchanged: 8bcc46f11556b926222ff46fabe79d26ee8bdeccd79a78f9b76da67f18555584",
    "defect C fixed: acceptance[].evidence_refs now resolves via _evidence_file_exists(evidence_directory, ref)",
    "defect D fixed: evidence_only exempts is_metrics_path, same predicate as scope_check",
    "evidence_only quadrants: evidence-dir-only=true, metrics-only=true, product-code=false, other-task-dir=false",
    "pre-fix reproduction in system temp: 3 target tests red, 2 guard tests green (Ran 5, failures=3)",
    "all five acceptance tests pass at the executor's actual test location",
    "contract command_ref for acceptance test 5 is not executable: AttributeError, exit 1",
    "end-to-end freshness: status=pass, errors=[], evidence_only=true, no 'evidence artifact missing', no 'product/test HEAD drifted'",
    "executor-result.json passes result verify with role executor",
    "pre-merge gate with executor only: blocked, errors are exactly the four missing review/final artifacts"
  ],
  "evidence_refs": [
    "review-report.md",
    "executor-report.md"
  ],
  "unverified": [
    "the frozen contract's test_ref for acceptance test 5 points outside allowed_paths; resolving it requires a derived planning task, not this round",
    "main-agent final check and finalization are not performed by this reviewer round"
  ]
}
```