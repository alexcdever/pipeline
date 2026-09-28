# 执行者报告：gate-deletion-semantics-continuation-1

## 一、任务身份

| 字段 | 值 |
|---|---|
| task_id | `gate-deletion-semantics-continuation-1` |
| task_type | `derived`（追补的派生记录单） |
| worktree | `D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1` |
| branch | `gate-deletion-semantics-continuation-1` |
| round | 1 |
| baseline head | `c92788c0ab9499faf950a3d403f11116dff90793`（`docs(tasks): freeze gate-deletion-semantics-continuation-1 record`） |
| 父任务 | `gate-deletion-semantics`（`prerequisite`，已合并，tip `1ed6c8b`） |

本任务是一张**追补的派生记录单**。它**不写新代码**，交付物是「核验任务单声称的既成交付确实成立」的只读结果与证据。任务单的 4 条验收测试全部指向**已经存在**的测试，本任务只真实运行它们并记录结果。

## 二、已确认事实的独立核验（6 项扩张 + 1 项契约内核心交付）

提交哈希在 `git log --oneline -12` 中全部真实存在（`12e302c`、`89835f0`、`b7ae0cc`、`8d677b0`、`2c88bad`）。

### 1. 4 条被删命令补回 `commands[]`（`89835f0`）

- 核验命令：`git show 89835f0 -- .pipeline/gate-deletion-semantics/review-report.md .pipeline/gate-deletion-semantics/final-check.md`
- 结论：**事实成立**。该提交在 `review-report.md` 补回 2 条、在 `final-check.md` 补回 2 条，共 4 条 `commands[]` 条目，均带 `expected_exit_code`：
  - `review-report.md`：新增 `scope history . --evidence-root .pipeline`（`exit_code 4, expected_exit_code 4`）与 `scope history . --evidence-root .pipeline --since 692ee63`（`exit_code 0`）。
  - `final-check.md`：新增 `scope history . --evidence-root .pipeline`（`exit_code 4, expected_exit_code 4`）与 `freshness ...`（`exit_code 3, expected_exit_code 3`）。
- 该提交同时新增正文小节「关于 `commands[]` 中的预期非零结果」解释为何保留而非删除。
- 任务单已知：**无既有测试断言这 4 条的存续**，故仅记录为事实（对应 `unknown-commands-array-restoration-has-no-test`）。

### 2. `expected_exit_code` 新字段（`89835f0`、`b7ae0cc`）

- 核验命令：`grep -n "expected_exit_code" pipeline_tools/core.py`
- 结论：**事实成立**。字段校验出现在两处：
  - `pipeline_tools/core.py:435-439`（`evidence_verify` 的 commands 循环）：读取 `expected_exit_code`，非 `int`（含 `bool`）即报 `expected_exit_code must be an integer`。
  - `pipeline_tools/core.py:1581-1590`（`gate_check`）：未声明时 `exit_code != 0` 报 `contains a non-zero command exit_code`；声明时 `exit_code != expected` 报 `exit_code does not match declared expected_exit_code`。
- `references/acceptance-evidence.md:13` 与 `templates/pipeline-evidence.json:14` 同步记录该字段语义。

### 3. 证据块解析取第一个闭标记（`89835f0`）

- 核验命令：`grep -n "def _read_machine_evidence\|def _machine_block" pipeline_tools/core.py pipeline_tools/reconcile.py`
- 结论：**事实成立**。两处实现均用 `next(...)` 取**第一个**闭标记，而非要求「恰好一个」闭标记：
  - `pipeline_tools/core.py:343-346`：`end = next((index for index in range(start + 1, len(lines)) if lines[index].strip() == "```"), None)`。
  - `pipeline_tools/reconcile.py:25`：`end = next((i for i in range(starts[0] + 1, len(lines)) if lines[i].strip() == "```"), None)`。
- 开标记仍要求**恰好一个**（`len(starts) != 1` 报 `missing or duplicate pipeline-evidence block`），闭标记只取第一个——这正是「取第一个闭标记」的语义。

### 4. `gate_check` 布尔边界守卫（`b7ae0cc`）

- 核验命令：`grep -n "isinstance(expected, bool)" pipeline_tools/core.py`
- 结论：**事实成立**。守卫为 `isinstance(expected, bool) or not isinstance(expected, int)`，出现在：
  - `pipeline_tools/core.py:437`（`evidence_verify`）
  - `pipeline_tools/core.py:1583`（`gate_check`）
- `exit_code` 同样有布尔守卫：`core.py:440`、`core.py:1589`（`isinstance(exit_code, bool) or exit_code != expected`）。因为 Python 中 `bool` 是 `int` 的子类，若不显式排除 `True`/`False`，它们会被当作 `1`/`0` 通过整数校验。

### 5. `.gitattributes` 新建（`b7ae0cc`、`8d677b0`）

- 核验命令：读 `.gitattributes` 全文；`git show b7ae0cc --stat`；`git show 8d677b0 --name-only`
- 结论：**事实成立**。`b7ae0cc` 首次加入 `.gitattributes`（3 行），`8d677b0` 再改为 4 行。当前内容与任务单「补充」一致：
  ```
  * text=auto eol=lf
  *.cmd text eol=crlf
  *.bat text eol=crlf
  docs/tasks/*.md -text
  ```
- 任务单已知：**无既有测试**读取 `.gitattributes` 或断言其 LF 策略（`grep -rn "gitattributes" tests/` 无命中），故仅记录为事实（对应 `unknown-gitattributes-has-no-test`）。

### 6. 15 个 `.pipeline/` 文件行尾规范化（`8d677b0`）

- 核验命令：`git show 8d677b0 --name-only --format=""`
- 结论：**事实成立**。`8d677b0`（`chore: normalize tracked line endings and protect task sheets`）改动 16 个文件，其中 1 个是 `.gitattributes` 本身，其余 **15 个为已跟踪的 `.pipeline/` 文件**：
  `derived-task-dispatch-recovery/finalization.json`、`dispatch-fail-closed-and-approval-semantics/finalization.json`、`evidence-finalization-atomicity/finalization.json`、`pipeline-evidence-lifecycle-migration-continuation-1/finalization.json`、`planning-driven-vertical-pipeline/executor-result.json`、`planning-driven-vertical-pipeline/finalization.json`、`planning-run-lifecycle/finalization.json`、`planning-run-task-generation/final-check.md`、`planning-run-task-generation/final-result.json`、`planning-run-task-generation/finalization.json`、`planning-to-dispatch-integration/finalization.json`、`repository-evidence-hygiene-continuation-5/finalization.json`、`task-plan-contract-consistency/finalization.json`、`task-worktree-dispatch-identity/finalization.json`、`task-worktree-dispatch-identity/review-report.md`。计数与任务单声称的 15 一致。
- 任务单已知：**无既有测试**断言重规范化或 eol（`grep -rn "renormalize\|line ending\|eol" tests/` 无命中），故仅记录为事实（对应 `unknown-line-ending-normalization-has-no-test`）。

### 契约内核心交付：删除语义修复（`12e302c`）

- 核验命令：`git show 12e302c --stat`；读 `pipeline_tools/core.py` 的 `commit_history_check`
- 结论：**事实成立**。`12e302c`（`fix(core): distinguish deletion from addition in evidence history check`）改动 `pipeline_tools/core.py`（+16/-? ），并新增 `tests/test_git_checks.py` 用例与 `references/acceptance-evidence.md` 说明。
- `core.py:252` 有 `deleting = status.startswith("D")`；`core.py:263` 有 `if retained == deleting:` —— 即「删除保留集文件」（`retained=True, deleting=True`）与「新增/修改非保留集文件」（`retained=False, deleting=False`）才报违规；「删除非保留证据」（`retained=False, deleting=True`）不再报违规。这正是删除方向的语义收窄。
- 该修复有既有测试（`tests/test_git_checks.py`），即验收测试4。

## 三、4 条验收测试运行记录

命令前缀 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`，工作目录为本 worktree。逐条实跑，均真实执行。

| # | 验收测试 | 命令 | exit code | 结果 |
|---|---|---|---|---|
| 1 | `acceptance-test-declared-expected-exit-code-allows-nonzero-result` | `python -m unittest tests.test_evidence.EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result` | 0 | OK（Ran 1 test in 0.022s） |
| 2 | `acceptance-test-gate-rejects-boolean-expected-exit-code` | `python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_boolean_expected_exit_code` | 0 | OK（Ran 1 test in 0.028s） |
| 3 | `acceptance-test-evidence-block-parses-with-other-code-fences` | `python -m unittest tests.test_evidence.EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences` | 0 | OK（Ran 1 test in 0.020s） |
| 4 | `acceptance-test-delete-non-retained-evidence-is-not-a-violation` | `python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation` | 0 | OK（Ran 1 test in 1.059s） |

任务单契约块的 `command_ref` 与实际运行命令一致，无差异。

## 四、全量测试

- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests`
- 结果：`Ran 275 tests in 187.571s` → `OK`，exit code `0`。
- 与基线 **275** 一致（主工作树合并后的值）。

## 五、本任务的性质声明

这是一张**记录单（record-only）**。本任务**不写新代码**、**不改产品语义**、**不改任何测试**。交付物是：

1. 本报告（核验结果）；
2. `executor-result.json`（机器结果）；
3. 上述 6 项扩张 + 1 项核心交付的独立核验证据；
4. 4 条既有验收测试的真实运行记录。

它对应用户「把终审裁定为『不违反 goal.md 但本应开派生单』的既成交付补记为一张可机械核验的 derived 任务单」的裁决。因此本报告**不声称任何用户可观察的功能完成**。

## 六、困难与解决

- **只读核验的写权限摩擦**：任务单把 `tests/test_evidence.py`、`tests/test_git_checks.py` 列为 operation 资源，模型中没有「只读资源」概念。本任务严格遵守 `non_goals`，只运行测试、不写入，`git status` 全程干净（除仓库常态的 `.pipeline/metrics/*.json` 事件）。
- **第 1/5/6 项无测试可跑**：这三项扩张没有任何既有测试可机械核验。按任务单裁决，本报告只以提交哈希与 `git show` 记录为事实，并如实标入 `unknowns`，不新建测试。
- **Python `bool` 是 `int` 子类**：第 4 项的布尔守卫必须显式 `isinstance(x, bool)`，否则 `True`/`False` 会被当作 `1`/`0` 放行。已读代码确认守卫存在。

## 七、未验证项

- 独立审查（`review-report.md`）——由审查子代理完成。
- 主代理终审（`final-check.md`）与合并——由主代理完成。
- `.gitattributes` 的实际行尾效果需要一次全新 clone 才能端到端验证；本任务只核验其存在与内容。

## 八、身份语义说明

`executor-result.json` 的 `identity.product_head` 与 `identity.head` 指向**本任务的执行提交**（产出本报告与其机器结果的提交），而不是 baseline `c92788c`。取值方式：先提交报告得到执行提交哈希，再把该哈希写入 `executor-result.json` 并提交。该 `product_head` 是最终 HEAD 的祖先，两者差异仅限本任务证据目录，满足 gate 的 evidence-only 约束。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "gate-deletion-semantics-continuation-1",
  "worktree": ".worktrees/gate-deletion-semantics-continuation-1",
  "branch": "gate-deletion-semantics-continuation-1",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "commands": [
    {"command": "git log --oneline -12", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "git show 12e302c --stat", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "git show 89835f0 --stat", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "git show b7ae0cc --stat", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "git show 8d677b0 --name-only --format=", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "grep -n \"expected_exit_code\" pipeline_tools/core.py", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_boolean_expected_exit_code", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"},
    {"command": "sha256sum docs/tasks/gate-deletion-semantics-continuation-1.md && git show c92788c:docs/tasks/gate-deletion-semantics-continuation-1.md | sha256sum", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1", "evidence_ref": "executor-report.md"}
  ],
  "assertions": [
    "All six scope-expansion commits (12e302c, 89835f0, b7ae0cc, 8d677b0, 2c88bad) exist in the reachable history of the worktree branch.",
    "commit_history_check distinguishes deletion from addition: core.py:252 has `deleting = status.startswith(\"D\")` and core.py:263 has `if retained == deleting:`.",
    "expected_exit_code is validated as an int in both evidence_verify (core.py:435-439) and gate_check (core.py:1581-1590).",
    "Both _read_machine_evidence (core.py:343-346) and _machine_block (reconcile.py:25) pick the first closing fence with next(...).",
    "The boolean boundary guard isinstance(expected, bool) or not isinstance(expected, int) exists at core.py:437 and core.py:1583.",
    ".gitattributes content matches the task sheet: '* text=auto eol=lf', '*.cmd text eol=crlf', '*.bat text eol=crlf', 'docs/tasks/*.md -text'.",
    "8d677b0 touches 16 files: .gitattributes plus 15 tracked .pipeline/ files.",
    "All four declared acceptance tests pass with exit code 0.",
    "Full suite: Ran 275 tests in 187.571s, OK, exit code 0.",
    "Task sheet sha256 is unchanged versus the frozen baseline commit c92788c."
  ],
  "evidence_refs": [
    "executor-report.md"
  ],
  "unverified": [
    "independent review (review-report.md) not performed in this round",
    "main-agent final check (final-check.md) and merge not performed in this round",
    ".gitattributes line-ending effect requires a fresh clone to validate end-to-end"
  ]
}
```