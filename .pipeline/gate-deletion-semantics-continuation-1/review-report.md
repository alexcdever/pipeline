# 审查报告：gate-deletion-semantics-continuation-1

## 一、审查身份

| 字段 | 值 |
|---|---|
| task_id | `gate-deletion-semantics-continuation-1` |
| role | `reviewer`（独立审查子代理） |
| worktree | `D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics-continuation-1` |
| branch | `gate-deletion-semantics-continuation-1` |
| round | 1 |
| 审查基线 | `c92788c`；执行提交 `5bf40a3`、`9f0e6cc`；审查时 HEAD = `9f0e6cc` |
| 审查方式 | 全部结论来自本审查子代理本轮直接运行或读取，未采信执行者自述 |

本任务是一张**手工撰写的派生记录单**（`task_type: derived`），「实现」不是写新代码，而是核验任务单声称的既成交付确实成立。因此审查重点是：6 项扩张是否真在 main 上、4 条验收测试是否真通过、执行者证据是否诚实完整。

---

## 二、提交与边界（A）

```
9f0e6cc fix(record): point executor identity at the execution commit
5bf40a3 verify(record): confirm derived delivery facts for gate-deletion-semantics
c92788c docs(tasks): freeze gate-deletion-semantics-continuation-1 record
1ed6c8b fix(evidence): record freshness failure in final check
9104afe final(gate-deletion): accept with adjudicated scope expansion
2c88bad docs(evidence): record line-ending normalization ruling
```

- `git show --stat 5bf40a3`：新增 `executor-report.md`（170 行）、`executor-result.json`（61 行）、`.pipeline/metrics/1790606515221168500-ec113624e8fa421fa9e5d820e8f9c845.json`，共 3 文件 232 行。
- `git show --stat 9f0e6cc`：仅改 `executor-result.json`（+2/-2），即把 identity 指向执行提交。
- `git status --short`：只有一个未跟踪的 `.pipeline/metrics/*.json`（自动化指标事件，常态，非本任务产物）。
- `git status --short --untracked-files=no`：**空**，无已跟踪改动。
- `git diff c92788c HEAD --name-status` 全部改动：
  - `A .pipeline/gate-deletion-semantics-continuation-1/executor-report.md`
  - `A .pipeline/gate-deletion-semantics-continuation-1/executor-result.json`
  - `A .pipeline/metrics/1790606515221168500-ec113624e8fa421fa9e5d820e8f9c845.json`

**禁止路径核验**：`git diff c92788c HEAD --name-status -- pipeline_tools tests references goal.md IDEA.md implement-plan.md docs/tasks/gate-deletion-semantics.md docs/tasks/gate-deletion-semantics-continuation-1.md` 输出为**空**，即这些路径在本任务期间**零改动**。合规。

**`.pipeline/metrics/` 删除核验**：`git show HEAD --name-status --diff-filter=D -- .pipeline/metrics/` 输出为**空**，未删除任何指标文件。合规。

**`forbidden_paths` 与 `.pipeline/**` 的矛盾（见第八节）**：`gate pre-merge` **不消费** `scope_check`，因此不会把交付文件报成 scope 违规。`gate_check`（`core.py:1534`）只调用 `evidence_verify` + 机器结果/状态/commands 检查 + git diff/冲突检查，没有 scope 校验路径。所以此矛盾未触发 gate 报错。

---

## 三、任务单字节未变（B）

```
sha256sum docs/tasks/gate-deletion-semantics-continuation-1.md
  → 1721091c5a2d7bb8776cce38e9c7bd9560e6d9f99ed6ca5198d9ca2b839b8129
git show c92788c:docs/tasks/gate-deletion-semantics-continuation-1.md | sha256sum
  → 1721091c5a2d7bb8776cce38e9c7bd9560e6d9f99ed6ca5198d9ca2b839b8129
```

两者一致，且等于任务单预期哈希。**冻结契约未被改动**，独立确认。

---

## 四、4 条验收测试独立实跑（C）

命令前缀 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`，工作目录为本 worktree。契约块 `command_ref` 与任务单正文给出的命令**完全一致**，无差异。

| # | 验收测试 | 独立实测 | exit code |
|---|---|---|---|
| 1 | `acceptance-test-declared-expected-exit-code-allows-nonzero-result` | Ran 1 test in 0.028s, OK | 0 |
| 2 | `acceptance-test-gate-rejects-boolean-expected-exit-code` | Ran 1 test in 0.033s, OK | 0 |
| 3 | `acceptance-test-evidence-block-parses-with-other-code-fences` | Ran 1 test in 0.026s, OK | 0 |
| 4 | `acceptance-test-delete-non-retained-evidence-is-not-a-violation` | Ran 1 test in 1.212s, OK | 0 |

**测试正文独立阅读**（不只看执行报告）：

- AT1（`tests/test_evidence.py:394-403`）：把 `report('reviewer')` 的 `"exit_code": 0` 替换为 `"exit_code": 4, "expected_exit_code": 4`，调 `gate_check(...pre-merge)`，断言无 `exit_code` 错误。**真实调用了 gate_check 的 expected_exit_code 分支**，非恒真断言。
- AT2（`tests/test_evidence.py:436-445`）：替换为 `"exit_code": 1, "expected_exit_code": true`，断言出现 `expected_exit_code` 错误。**确实覆盖布尔守卫**（`true` 在 Python 中是 `True`，会被当 `1` 放行，除非显式 `isinstance(expected, bool)`）。
- AT3（`tests/test_evidence.py:366-378`）：报告正文里插了 ```` ```python ```` 代码围栏，断言 `evidence_verify` 不报 `closed`。**覆盖「取第一个闭标记」语义**：若不取第一个闭标记而取正文里的闭标记，解析会截断在错误的 `` ``` `` 上。
- AT4（`tests/test_git_checks.py:165-178`）：真实 `git init` 一个临时仓库，提交 `scratch.log`（非保留证据）后删除，断言 `commit_history_check(... since=baseline) == []`。**真实 Git 边界，非 mock**。配套 `test_delete_retained_evidence_is_a_violation`（:180-195）证明保留集删除仍报违规，构成方向对照。

**全量测试**：`python -m unittest discover -s tests` → `Ran 275 tests in 208.916s` → `OK`，管道退出码 0。与基线 275 一致，无新增/遗漏用例。

> 说明：全量输出尾部的 `{"duration_s": 0.031, "exit_code": 1, ...}` 是某个用例内部自跑的 `tmp` 子进程探针日志（它测的正是「非零退出码被正确捕获」），不是 unittest 主进程的退出码；unittest 自身报告 `OK`，`pipe_exit=0`。

---

## 五、6 项扩张独立核验（D）

逐项贴原文/行号，全部为本审查子代理独立读取 `main` 上代码所得。

| # | 扩张 | 提交 | 独立核验结果 |
|---|---|---|---|
| — | 删除语义修复（契约内核心） | `12e302c` | **成立** |
| 1 | 4 条被删命令补回 `commands[]` | `89835f0` | **成立** |
| 2 | `expected_exit_code` 新字段 | `89835f0`、`b7ae0cc` | **成立** |
| 3 | 证据块解析取第一个闭标记 | `89835f0` | **成立** |
| 4 | `gate_check` 布尔边界守卫 | `b7ae0cc` | **成立** |
| 5 | `.gitattributes` 新建 | `b7ae0cc`、`8d677b0` | **成立**（仅记录事实，无测试） |
| 6 | 15 个 `.pipeline/` 文件行尾规范化 | `8d677b0` | **成立**（仅记录事实，无测试） |

### 1. 删除语义修复（`12e302c`）

`pipeline_tools/core.py` 原文：

- `core.py:252`：`deleting = status.startswith("D")`
- `core.py:262`：`retained = Path(normalized).name in RETAINED_EVIDENCE_NAMES`
- `core.py:263`：`if retained == deleting:`

语义：`retained == deleting` 为真才报违规 → 只有「删除保留集文件」（`retained=True, deleting=True`）与「新增/修改非保留集文件」（`retained=False, deleting=False`）报违规；「删除非保留证据」（`retained=False, deleting=True`）不再报违规。正是删除方向的收窄。

### 2. `expected_exit_code` 新字段

`grep -n "expected_exit_code" pipeline_tools/core.py` 命中：

- `core.py:435`：`expected = command.get("expected_exit_code")`（`evidence_verify` 内）
- `core.py:439`：`errors.append(f"{name} command {index} expected_exit_code must be an integer")`
- `core.py:1581`：`expected = command.get("expected_exit_code")`（`gate_check` 内）
- `core.py:1585`：`... expected_exit_code must be an integer`
- `core.py:1590`：`... exit_code does not match declared expected_exit_code`

两处校验**均存在**。`gate_check` 的完整分支：`expected is None → exit_code != 0 报错`；`expected 已声明 → exit_code != expected 报错`。

### 3. 证据块解析取第一个闭标记

- `core.py:343-346`（`_read_machine_evidence`）：`end = next((index for index in range(start + 1, len(lines)) if lines[index].strip() == "```"), None)`
- `reconcile.py:25`（`_machine_block`）：`end = next((i for i in range(starts[0] + 1, len(lines)) if lines[i].strip() == "```"), None)`

两处**均用 `next(...)` 取第一个闭标记**。开标记仍要求恰好一个（`len(starts) != 1` 报 `missing or duplicate pipeline-evidence block`），闭标记只取第一个——与任务单描述一致。

### 4. `gate_check` 布尔边界守卫

- `core.py:437`：`isinstance(expected, bool) or not isinstance(expected, int)`
- `core.py:1583`：`isinstance(expected, bool) or not isinstance(expected, int)`
- 另有 exit_code 守卫：`core.py:1589`：`elif isinstance(exit_code, bool) or exit_code != expected:`

**成立**。因 Python `bool` 是 `int` 子类，不显式排除 `True`/`False` 会被当作 `1`/`0` 放行。

### 5. `.gitattributes`（`b7ae0cc`、`8d677b0`）

`cat -A .gitattributes` 原文（`$` 为行尾）：

```
* text=auto eol=lf$
*.cmd text eol=crlf$
*.bat text eol=crlf$
docs/tasks/*.md -text
```

4 行，与任务单「补充」逐字一致。`b7ae0cc` 首次加入（3 行），`8d677b0` 改为 4 行。**仅记录为事实**：`grep -rn "gitattributes" tests/` 无命中。

### 6. 15 个 `.pipeline/` 文件行尾规范化（`8d677b0`）

`git show 8d677b0 --name-only --format="" | wc -l` → **16**。逐条：

```
.gitattributes
.pipeline/derived-task-dispatch-recovery/finalization.json
.pipeline/dispatch-fail-closed-and-approval-semantics/finalization.json
.pipeline/evidence-finalization-atomicity/finalization.json
.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json
.pipeline/planning-driven-vertical-pipeline/executor-result.json
.pipeline/planning-driven-vertical-pipeline/finalization.json
.pipeline/planning-run-lifecycle/finalization.json
.pipeline/planning-run-task-generation/final-check.md
.pipeline/planning-run-task-generation/final-result.json
.pipeline/planning-run-task-generation/finalization.json
.pipeline/planning-to-dispatch-integration/finalization.json
.pipeline/repository-evidence-hygiene-continuation-5/finalization.json
.pipeline/task-plan-contract-consistency/finalization.json
.pipeline/task-worktree-dispatch-identity/finalization.json
.pipeline/task-worktree-dispatch-identity/review-report.md
```

`.gitattributes` + **15 个** `.pipeline/` 文件 = 16。计数与任务单声称的 15 一致。**仅记录为事实**：`grep -rn "renormalize\|line ending\|eol" tests/` 无命中。

---

## 六、证据文件合规性（E）

### 目录内容

`.pipeline/gate-deletion-semantics-continuation-1/`：

| 文件 | 大小 |
|---|---|
| `executor-report.md` | 15537 字节 |
| `executor-result.json` | 2192 字节 |

### `executor-report.md`

- `grep -c '^```pipeline-evidence'` → **1**（恰好一个，且是逐字 `pipeline-evidence`，非 `json`）。
- 围栏位置：第 126 行开、第 170 行闭，位于文件末尾。
- 块内 JSON 合法（本审查子代理 `json.loads` 成功）。
- 逐字段核验：`schema`=1 ✓、`task_id` 正确 ✓、`worktree`=`.worktrees/gate-deletion-semantics-continuation-1` ✓、`branch` 正确 ✓、`role`=`executor` ✓、`round`=1 ✓、`status`=`PASS` ✓（∈{PASS,READY-TO-MERGE}）、`commands` 非空 ✓、`assertions` 非空字符串数组 ✓、`evidence_refs`=`["executor-report.md"]` 存在 ✓、`unverified` 为数组 ✓。
- `commands[]`：**12 条**，每条有非空 `command`、整数 `exit_code`、`evidence_ref`。**非零 exit_code 数量 = 0**（全部 0）。
- `assertions`：**10 条**，全部非空。
- `evidence_refs` 引用的 `executor-report.md` 真实存在于证据目录。

### `executor-result.json`

- JSON 合法。
- `identity`：`product_head`=`5bf40a3b0971d0a6dbb1ca07aff864f348660f74`、`head`=同、`branch`=`gate-deletion-semantics-continuation-1`、`worktree`=本 worktree 绝对路径。
- `acceptance`：4 条，全部 `status: pass`、`exit_code: 0`。
- `unverified`：5 条（independent review / main-agent final check / merge to main / post-merge gate / gitattributes fresh-clone）。

### 与执行者自述核对

执行者报告第七节/结果文件称 `commands[]` 12 条全部 exit 0、`assertions` 10 条。**实测完全吻合**：12 条命令、10 条断言、零非零退出码。此两处自述**属实**。

---

## 七、执行者两处已知问题的独立评估（F）

### F1：`freshness` 失败未报告

独立实跑：

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json \
  freshness . .pipeline/gate-deletion-semantics-continuation-1 \
  --result .pipeline/gate-deletion-semantics-continuation-1/executor-result.json
```

实测结果：`status: "blocked"`、**exit 3**、`errors: ["evidence artifact missing"]`、`observed` 含 `evidence_only: true`、`changed_paths: [".pipeline/.../executor-result.json"]`、`product_head: 5bf40a3...`、`head: 9f0e6cc...`。与任务单预期一致。

**根因独立确认**（读代码）：`core.py:1402-1407` 对 `result["acceptance"][].evidence_refs` 逐个用 `candidate = root / reference` 解析——即按**仓库根相对路径**；而 `commands[].evidence_ref` 走 `_evidence_file_exists`（`core.py:305-317`），该函数对**不以 `.pipeline/` 开头**的裸文件名回退到**证据目录**解析。`executor-result.json` 的 `acceptance[].evidence_refs = ["executor-report.md"]` 是裸名，在仓库根下不存在 → 报 `evidence artifact missing`。同一个字段名两种解析基准，**确为工具缺陷**，且是**全仓库既有约定**（父任务 `final-check.md` 第 140 行已记载同一现象）。

**严重性评估**：**中等偏低，但属实质报告缺口。**

- 执行者报告**全文未提**这次失败；其 `commands[]` 里也没有 freshness 命令。它与父任务终审（`1ed6c8c`、`final-check.md:130-144`）形成对比——父任务终审**主动如实记录**了同一 freshness 失败。
- 缓解因素：（a）该缺陷是工具的既有问题，不是本任务引入；（b）`gate pre-merge` **不消费** `freshness`，故不阻塞合并；（c）本任务的性质是记录单，freshness 失败不改变「6 项扩张成立、4 测试通过」的结论。
- 但按 `references/execution-and-review.md`「报告按观察/结论/未验证项区分」「无法读取时必须标 BLOCKED/未验证」的要求，执行者**应当记录**这次已实际触及的失败。未记录使报告**不完整**，削弱了它作为独立证据的可信度——尤其考虑到执行代理此前多次误报的历史。
- **结论**：不改变本任务的交付结论（事实仍成立），但构成对执行者报告完整性的负面记录，应在主代理终审中显式补记。

### F2：`product_head != HEAD`

- `git diff 5bf40a3 9f0e6cc --name-only` → 仅 `.pipeline/gate-deletion-semantics-continuation-1/executor-result.json`（1 文件）。
- `git merge-base --is-ancestor 5bf40a3 HEAD; echo $?` → **0**，`5bf40a3` 是 HEAD 的祖先。
- `evidence_freshness` 的 `evidence_only` 判定（`core.py:1386-1396`）：对 `product_head..current_head` 的 `changed_paths` 逐条判断是否都落在 `evidence_root` 内 → 实测 `evidence_only: true`。

**判断：执行者的处置可接受。** 理由：

1. 写入 `identity.product_head` 的提交本身会改变 HEAD——要求 `product_head == HEAD` 是**自指悖论**：任何把自身哈希写入结果的提交都会使两者不等。
2. 差异严格限于证据目录内 1 个文件，`evidence_only: true` 成立，满足工具对「产品/测试 HEAD 未漂移」的判定（`core.py:1394-1396`）。
3. `identity.head` 在 `9f0e6cc` 里已更新为 `5bf40a3` 与 HEAD 一致（读结果文件确认），即执行者把 `head` 指向了执行提交。gate 的 `identity.head != current_head` 检查（`core.py:1400`）此时会看到 `head=5bf40a3` 而 `current_head=9f0e6cc`……

> **注意**：`result verify` 本轮对 `executor-result.json` 返回 `pass / exit 0`，说明它不强制 `identity.head == HEAD`。但 `evidence_freshness` 走的是 `product_head` 分支（因为它优先看 `product_head`），判 `evidence_only: true` 后不报 `product/test HEAD drifted`。因此 F2 在本工具链下**不产生错误**，处置可接受。

---

## 八、`forbidden_paths` 与 `.pipeline/**` 的矛盾评估

契约块 `forbidden_paths` 明列 `.pipeline/**`（第 44 行），而本任务的两份交付文件**都在** `.pipeline/gate-deletion-semantics-continuation-1/` 下，`git diff c92788c HEAD` 也确实新增了 `.pipeline/` 下文件。

**评估：这是契约缺陷，且未被 gate 捕获。**

1. **为什么未触发 gate**：独立读 `core.py:1534-1605` 的 `gate_check`，它**不调用** `scope_check`。scope 校验只在 `__main__.py:1020-1021`（��立的 `scope check` 子命令）和 `role_scope_check` 中发生，且 `scope check` 要求显式传 `--allowed`，不会自动从任务单契约读 `forbidden_paths`。所以 `gate pre-merge` 不会因 `.pipeline/**` 报 scope 违规——实测 `gate pre-merge` 只报缺 4 份文件。
2. **矛盾的实质**：派生记录型任务的**证据目录本身就是交付物**，而契约把 `.pipeline/**` 整片列为禁止。这意味着若某条流程真去执行 `scope_check`，本任务的合法交付会被判违规。任务单正文（第 217、222 行）已声明「本任务只读」，但 `forbidden_paths` 的机械语义与之冲突。
3. **影响面**：目前 gate 不消费 scope，所以**不阻塞合并**；但这是「记录型任务的证据目录与 forbidden 列表自相矛盾」的结构性问题，应作为契约设计缺陷上报。建议在后续修复中让 `forbidden_paths` 支持豁免任务自身的证据目录，或让 gate 把自身证据目录排除在 scope 之外。

---

## 九、执行两阶段之外的未做项

按 `references/execution-and-review.md`「主代理最终检查」一节，本任务当前**只有执行者报告 + 本审查报告**，尚缺：

- `final-check.md`（主代理终审）
- `final-result.json`（主代理终审机器结果）

两阶段之外的未做项还包括：合并、post-merge gate、finalization（清理非保留证据）。这些**不属于审查子代理职责**，如实列出。

本报告**不引用任何已删除的原始日志**（符合 `goal.md:51`）：所有证据均来自本 worktree 当前可读的文件、当前 Git 对象和本轮直接运行的命令输出。

---

## 十、与执行者自述不符之处

1. **F1**：执行者未报告 `freshness` 的 blocked/exit 3 失败。其 `commands[]` 无 freshness 条目，报告正文亦未提。**属实的不完整**（该失败真实存在，本轮实测复现）。
2. 其余自述（6 项扩张成立、4 测试通过、12 命令全 0、10 断言、275 全量 OK、任务单哈希未变、`8d677b0` 触及 16 文件）**逐项独立复核后全部属实**，无不符。

---

## 十一、总体结论

**ACCEPT WITH CONDITIONS。**

- 4 条验收测试独立实跑 **4/4 通过**，全量 275 tests OK。
- 6 项扩张 + 1 项契约内核心交付 **逐项独立核验成立**，行号/原文均已贴出。
- 任务单冻结字节未变，禁止路径零改动，metrics 零删除。
- 执行者 `commands[]`/`assertions` 计数自述属实。

**条件**：

1. 主代理终审必须**补记 F1**（`freshness` blocked/exit 3），不得据执行者报告判「freshness 通过」。
2. 必须把 **`forbidden_paths` 含 `.pipeline/**` 与记录型任务证据目录的矛盾**作为契约缺陷上报（gate 当前不消费 scope，故不阻塞，但机制上矛盾）。
3. F2（`product_head != HEAD`）判定为**可接受**，无需整改，但应记录理由（自指悖论 + evidence_only 成立）。

---

```pipeline-evidence
{
  "schema": 1,
  "task_id": "gate-deletion-semantics-continuation-1",
  "worktree": ".worktrees/gate-deletion-semantics-continuation-1",
  "branch": "gate-deletion-semantics-continuation-1",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "commands": [
    {"command": "sha256sum docs/tasks/gate-deletion-semantics-continuation-1.md && git show c92788c:docs/tasks/gate-deletion-semantics-continuation-1.md | sha256sum", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "git diff c92788c HEAD --name-status -- pipeline_tools tests references goal.md IDEA.md implement-plan.md docs/tasks/gate-deletion-semantics.md docs/tasks/gate-deletion-semantics-continuation-1.md", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "git show HEAD --name-status --diff-filter=D -- .pipeline/metrics/", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "grep -n \"expected_exit_code\" pipeline_tools/core.py", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "grep -n \"isinstance(expected, bool)\" pipeline_tools/core.py", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "git show 8d677b0 --name-only --format=\"\" | wc -l", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_boolean_expected_exit_code", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_evidence.EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0, "evidence_ref": "review-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/gate-deletion-semantics-continuation-1 --result .pipeline/gate-deletion-semantics-continuation-1/executor-result.json", "exit_code": 3, "expected_exit_code": 3, "evidence_ref": "review-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/gate-deletion-semantics-continuation-1 --task-id gate-deletion-semantics-continuation-1", "exit_code": 3, "expected_exit_code": 3, "evidence_ref": "review-report.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/gate-deletion-semantics-continuation-1/executor-result.json --task-id gate-deletion-semantics-continuation-1 --role executor", "exit_code": 0, "evidence_ref": "review-report.md"}
  ],
  "assertions": [
    "All four acceptance tests pass independently with exit code 0 (AT1 0.028s, AT2 0.033s, AT3 0.026s, AT4 1.212s).",
    "Full suite ran 275 tests in 208.916s with result OK and exit code 0.",
    "Task sheet sha256 is 1721091c5a2d7bb8776cce38e9c7bd9560e6d9f99ed6ca5198d9ca2b839b8129, identical to the c92788c baseline blob.",
    "No forbidden path (pipeline_tools/**, tests/**, references/**, goal.md, IDEA.md, implement-plan.md, docs/tasks/gate-deletion-semantics.md, the frozen task sheet) changed between c92788c and HEAD.",
    "No .pipeline/metrics/ file was deleted in HEAD.",
    "core.py:252 has deleting = status.startswith(\"D\") and core.py:263 has if retained == deleting:.",
    "expected_exit_code is validated at core.py:435/439 (evidence_verify) and core.py:1581/1585/1590 (gate_check).",
    "First-closing-fence selection via next(...) exists at core.py:343-346 and reconcile.py:25.",
    "Boolean guard isinstance(expected, bool) or not isinstance(expected, int) exists at core.py:437 and core.py:1583, plus exit_code guard at core.py:1589.",
    ".gitattributes has exactly 4 lines: '* text=auto eol=lf', '*.cmd text eol=crlf', '*.bat text eol=crlf', 'docs/tasks/*.md -text'.",
    "8d677b0 touches 16 files: .gitattributes plus 15 tracked .pipeline/ files.",
    "executor-report.md contains exactly one ```pipeline-evidence block at lines 126-170 with a valid JSON object and role executor.",
    "executor-report.md commands[] has 12 entries all with exit_code 0; assertions has 10 non-empty strings; both match the executor's self-report.",
    "freshness returns status blocked, exit 3, errors [evidence artifact missing], evidence_only true; the executor did not report this failure.",
    "5bf40a3 is an ancestor of HEAD (merge-base --is-ancestor exit 0) and 5bf40a3..9f0e6cc differs only in .pipeline/gate-deletion-semantics-continuation-1/executor-result.json.",
    "gate pre-merge reports blocked with exactly four missing artifacts: review-report.md, final-check.md, reviewer-result.json, final-result.json.",
    "gate_check does not consume scope_check, so the .pipeline/** forbidden_paths contradiction is not raised by the gate."
  ],
  "evidence_refs": [
    "review-report.md"
  ],
  "unverified": [
    "main-agent final check (final-check.md) not performed in this round",
    "merge to main and post-merge gate not performed in this round",
    "finalization of the evidence directory not performed in this round",
    ".gitattributes line-ending effect requires a fresh clone to validate end-to-end"
  ]
}
```