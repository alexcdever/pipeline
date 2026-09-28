# 主代理终审：gate-deletion-semantics-continuation-1

## 任务身份

- 任务单：`docs/tasks/gate-deletion-semantics-continuation-1.md`
- task-id：`gate-deletion-semantics-continuation-1`
- task_type：`derived`（追补父任务 `gate-deletion-semantics` 的契约外扩张）
- worktree：`.worktrees/gate-deletion-semantics-continuation-1`
- branch：`gate-deletion-semantics-continuation-1`
- 冻结基线：`c92788c`（手工冻结的任务单）
- 终审执行者角色：`main-final`

本任务不交付新代码；它的「实现」是核验任务单所声称的事实。终审按 `references/execution-and-review.md` 的「主代理最终检查」执行，独立复核，不抄执行者或审查者的摘要。

## 一、F1 补记：freshness 检查 blocked（执行者未报告）

### 1.1 实测命令与原文输出

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/gate-deletion-semantics-continuation-1 --result .pipeline/gate-deletion-semantics-continuation-1/executor-result.json
EXIT=3
```

原文输出（节选关键字段）：

```json
{
  "command": "evidence.freshness",
  "status": "blocked",
  "errors": ["product/test HEAD drifted", "evidence artifact missing"],
  "observed": [
    {"fact": "head", "value": "ba5e8bbfd41851496134e5de81b313a1cc0f252c"},
    {"fact": "product_head", "value": "5bf40a3b0971d0a6dbb1ca07aff864f348660f74"},
    {"fact": "changed_paths", "value": [
      ".pipeline/gate-deletion-semantics-continuation-1/executor-result.json",
      ".pipeline/gate-deletion-semantics-continuation-1/review-report.md",
      ".pipeline/gate-deletion-semantics-continuation-1/reviewer-result.json",
      ".pipeline/metrics/1790606895641684700-c098a580bef54d61b0e3d2f54b037aeb.json",
      ".pipeline/metrics/1790607379915245800-d921911ddb664d1ea0a94ce5bb23d311.json"
    ]},
    {"fact": "evidence_only", "value": false}
  ]
}
```

**与审查者快照的差异（如实记录）**：独立审查在 `9f0e6cc` 处复现到的是**一条** error（`evidence artifact missing`），`evidence_only: true`。终审在 `ba5e8bb` 处得到**两条** error，`evidence_only: false`。差异的唯一来源是审查提交 `ba5e8bb` 自身新增了两个 `.pipeline/metrics/*.json` 文件——它们落在**证据目录之外**，于是 `evidence_only` 由 true 翻转为 false，追加了 `product/test HEAD drifted`。两个观察都不矛盾，只是 HEAD 不同；下面分别给出两条 error 的根因。

### 1.2 根因（含行号）

**根因 A — `evidence artifact missing`（同一字段名两种基准）**

- `pipeline_tools/core.py:1347` `def evidence_freshness(root, evidence_directory, result_path=None)`
- `pipeline_tools/core.py:1396-1407`：对 `acceptance[].evidence_refs` 逐条用 **仓库根相对** 解析：
  - `core.py:1403` `candidate = root / reference.replace("\\", "/")`
  - `core.py:1407` `errors.append("evidence artifact missing")`
  - 本单 `executor-result.json` 的 `acceptance[].evidence_refs` 是裸名 `"executor-report.md"`，于是被拼成 `<仓库根>/executor-report.md`，不存在 → 报缺失。
- `pipeline_tools/core.py:313-325` `def _evidence_file_exists(directory, reference)`：对 `commands[].evidence_ref` 用 **证据目录相对**（`base = evidence_directory`，裸名直接落在证据目录下）。
- 同一个 `evidence_ref` 字段名，在两处用了两种基准。因此证据块里 12 条命令的裸名 `evidence_ref` 全部通过 `_evidence_file_exists`，而同一批文件以 `acceptance[].evidence_refs` 形式出现时却判缺失。

**根因 B — `product/test HEAD drifted`（metrics 未豁免）**

- `pipeline_tools/core.py:1385-1393`：`evidence_only` 要求 `product_head..HEAD` 的**全部** changed_paths 都落在证据目录 `evidence_root` 内；否则 `core.py:1393` 追加 `"product/test HEAD drifted"`。
- 该判定不豁免 `.pipeline/metrics/`。而工具在别处明确把 metrics 当作「工作流元数据、不属于产品范围」——见 `core.py:277-281` 的 `scope_check` 注释与豁免逻辑。两处口径不一致。
- 后果：**审查提交本身**（合法地只写入证据与 metrics）也会触发 drift，这是自指的假阳性。

### 1.3 为何非本任务引入

- 上述两段代码在基线 `c92788c` 之前就已存在，属工具既有缺陷。本单 `allowed_paths` 不含 `pipeline_tools/**`，`non_goals` 第 4 条明写「不修改 `pipeline_tools/` 的任何语义或实现」；本任务全程只读，未改任何工具代码（`git diff c92788c HEAD --name-status` 证明：改动仅 4 个 `.pipeline/<task-id>/` 证据文件 + 3 个 `.pipeline/metrics/` 文件，见 1.4）。
- 因此 freshness 失败既不是本单交付引入的回归，也不是本单可以就地修复的。

### 1.4 为何不阻塞本任务

- `gate pre-merge` **不消费** `freshness`。`gate_check`（`core.py:1534`）的调用清单为：`evidence_verify`、`implement_plan_status`、`_read_machine_evidence`、`_machine_result_errors`、`git diff --check`、`git ls-files -u`、`git rev-parse --verify HEAD`、`_post_merge_reverified_in_main_worktree`（post-merge）。其中没有任何一处调用 `evidence_freshness`。
- 终审实测 `gate pre-merge` 在补齐 `final-check.md` / `final-result.json` 后返回 pass/exit 0（见第六节）。

### 1.5 明确裁定

**不得据执行者报告判「freshness 通过」。** 执行者的 `executor-report.md` 与 `executor-result.json` 都没有记录这次失败：`commands[]` 中没有 freshness 条目，`verified_facts` 与 `unverified` 也从未提及。这是一处**报告完整性缺口**——执行者漏报了一个在其自身 HEAD 上可复现的失败检查。审查者已独立复现并在 `reviewer-result.json` 的 `executor_self_report_discrepancies` 中记录；终审独立复跑再次确认，并额外发现 `ba5e8bb` 之后 error 变为两条。

## 二、F2 裁定：`identity.product_head = 5bf40a3` 可接受

### 2.1 独立核验

```
git diff 5bf40a3 9f0e6cc --name-only
→ .pipeline/gate-deletion-semantics-continuation-1/executor-result.json   （仅 1 个文件）

git merge-base --is-ancestor 5bf40a3 HEAD; echo $?
→ 0        （5bf40a3 是 HEAD 的祖先）
```

`9f0e6cc`（`fix(record): point executor identity at the execution commit`）的 `--stat` 也印证：只改 `executor-result.json` 2 行（`product_head` 与 `head`）。

### 2.2 `evidence_only` 判定逻辑的行号

`pipeline_tools/core.py:1385-1393`（`evidence_freshness` 内）：

- `core.py:1386-1390`：把 `evidence_directory` 相对仓库根解析为 `evidence_root`；
- `core.py:1391-1393`：`evidence_only = bool(evidence_root) and all(path == evidence_root or path.startswith(evidence_root + "/") for path in changed_paths)`，不满足即 `errors.append("product/test HEAD drifted")`（`core.py:1393`）。

在 `9f0e6cc` 处 `5bf40a3..9f0e6cc` 只差 `executor-result.json`（在证据目录内），故 `evidence_only: true` 实测成立。

### 2.3 裁定

**可接受。** 理由两条：

1. `evidence_only: true` 在 `9f0e6cc` 实测成立——两者之间的唯一差异位于证据目录内。
2. 写入 identity 的提交本身就会推进 HEAD。要求 `product_head == HEAD` 是自指悖论：`9f0e6cc` 正是「把 `product_head` 指向被报告的执行提交」的提交，若同时要求它等于 HEAD，则该提交无法存在。因此 `product_head` 指向被报告的执行提交 `5bf40a3`、而 HEAD 落在其后的证据提交上，是正确语义。

## 三、`forbidden_paths` 契约缺陷上报

### 3.1 事实

本单契约 `forbidden_paths` 含 `.pipeline/**`（任务单第 44 行），而本单的**全部交付文件**都在 `.pipeline/gate-deletion-semantics-continuation-1/` 下。这是一张记录型任务：它的证据目录与它的 forbidden 列表互相矛盾。

### 3.2 `gate_check` 是否调用 `scope_check` —— 调用清单

`pipeline_tools/core.py:1534` 起的 `gate_check` 体内，实际发生的调用只有：

| 位置（相对 1534） | 调用 |
|---|---|
| +29 | `evidence_verify(directory, task_id, branch)` |
| +35 | `implement_plan_status(root, contract, task_id)` |
| +41 | `_read_machine_evidence(directory / name)` |
| +45 | `_machine_result_errors(directory, phase)` |
| +72 | `git(root, "diff", "--check")` |
| +75 | `git(root, "ls-files", "-u")` |
| +81 | `git(root, "rev-parse", "--verify", "HEAD")`（仅 post-merge） |
| +84 | `_post_merge_reverified_in_main_worktree(...)`（仅 post-merge） |

**结论：`gate_check` 不调用 `scope_check`。** 契约里的 `allowed_paths` / `forbidden_paths` 在 gate 阶段完全不被机械校验。

### 3.3 `scope check` 子命令是否需显式 `--allowed`

需要。`pipeline_tools/__main__.py:76-78` 的 `_add_scope_args`：

```python
parser.add_argument("--allowed", action="append", nargs="+", required=True)
parser.add_argument("--forbidden", action="append", nargs="*", default=[])
```

`--allowed` 是 `required=True`。也就是说 `scope check` **不会**自动从任务单契约读取 `allowed_paths`/`forbidden_paths`，调用方必须显式传入。`__main__.py:1018-1021` 只是把 `args.allowed` / `args.forbidden` 展平后交给 `scope_check`。

### 3.4 裁定

这是**契约设计缺陷**：记录型任务的证据目录（`.pipeline/<task-id>/`）与其 `forbidden_paths`（`.pipeline/**`）自相矛盾；而因为 `gate_check` 根本不跑 `scope_check`，该矛盾**当前不阻塞**。应上报为已知项：要么让 gate 消费契约的 scope，要么为记录型任务定义「证据目录白名单」。

## 四、`evidence_refs` 修复归属：须另开任务

### 4.1 原文核验

- 本单 `allowed_paths`（任务单第 33-37 行）只有 3 项：`docs/tasks/gate-deletion-semantics-continuation-1.md`、`tests/test_evidence.py`、`tests/test_git_checks.py`。**不含 `pipeline_tools/**`。**
- 本单 `non_goals` 第 4 条（任务单第 28 行）：「不修改 `pipeline_tools/` 的任何语义或实现」。

两条均在冻结任务单中逐字确认。

### 4.2 裁定

用户已裁决 `evidence_refs` 的修复方向是「改工具，统一按证据目录」（即修 F1 根因 A）。该修复**不在本任务范围内**——它需要改 `pipeline_tools/core.py`，而该路径既不在 `allowed_paths`，又被 `non_goals` 明令禁止。

**该修复须另开任务**，方式与父任务处理 `--since` 语义缺陷一致：以派生任务单承载工具修复，附独立验收测试。

## 五、核心事实独立复核（未抄任何摘要）

### 5.1 Git

```
git log --oneline -8
ba5e8bb review(record): independent verification of gate-deletion-semantics derived record
9f0e6cc fix(record): point executor identity at the execution commit
5bf40a3 verify(record): confirm derived delivery facts for gate-deletion-semantics
c92788c docs(tasks): freeze gate-deletion-semantics-continuation-1 record
1ed6c8b fix(evidence): record freshness failure in final check
9104afe final(gate-deletion): accept with adjudicated scope expansion
2c88bad docs(evidence): record line-ending normalization ruling
8d677b0 chore: normalize tracked line endings and protect task sheets
```

```
git show --stat 5bf40a3  → 3 files, +232（executor-report.md / executor-result.json / 1 metrics）
git show --stat 9f0e6cc  → 1 file, +2/-2（executor-result.json）
git show --stat ba5e8bb  → 4 files, +421（review-report.md / reviewer-result.json / 2 metrics）
```

```
git status --short            → 空
git status --short -uno       → 空
git diff c92788c HEAD --name-status
A .pipeline/gate-deletion-semantics-continuation-1/executor-report.md
A .pipeline/gate-deletion-semantics-continuation-1/executor-result.json
A .pipeline/gate-deletion-semantics-continuation-1/review-report.md
A .pipeline/gate-deletion-semantics-continuation-1/reviewer-result.json
A .pipeline/metrics/1790606515221168500-ec113624e8fa421fa9e5d820e8f9c845.json
A .pipeline/metrics/1790606895641684700-c098a580bef54d61b0e3d2f54b037aeb.json
A .pipeline/metrics/1790607379915245800-d921911ddb664d1ea0a94ce5bb23d311.json
```

全部为新增（`A`），无删除、无修改；禁止路径零改动；`.pipeline/metrics/` 无删除。

### 5.2 四条 acceptance（逐条实跑，exit code 记录）

| # | 命令 | exit |
|---|---|---|
| 1 | `python -m unittest tests.test_evidence.EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result` | 0（Ran 1 test OK） |
| 2 | `python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_boolean_expected_exit_code` | 0（Ran 1 test OK） |
| 3 | `python -m unittest tests.test_evidence.EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences` | 0（Ran 1 test OK） |
| 4 | `python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation` | 0（Ran 1 test OK） |

4/4 通过。

### 5.3 全量测试

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests
→ Ran 275 tests in 200.718s
→ OK
→ exit 0
```

与基线 275 一致（终审实跑数字：275，200.718s）。

### 5.4 任务单字节未变

```
sha256sum docs/tasks/gate-deletion-semantics-continuation-1.md
→ 1721091c5a2d7bb8776cce38e9c7bd9560e6d9f99ed6ca5198d9ca2b839b8129
```

与冻结基线一致，任务单字节未变。

### 5.5 三项扩张抽查（自查代码）

1. **删除语义**：`core.py:252` `deleting = status.startswith("D")`；`core.py:263` `if retained == deleting:` → `commit_history_check` 仅在「删除了保留文件」或「新增/修改了非保留文件」时报违规，`D` 与 `A` 区分成立。
2. **`expected_exit_code` 与布尔守卫**：`evidence_verify` 在 `core.py:435-441` 校验 `expected_exit_code` 必须是整数、`exit_code` 必须是数字；`gate_check` 在 `core.py:1581-1590` 再做一遍（`isinstance(expected, bool) or not isinstance(expected, int)` → 报错；`expected is None` 时非零即报错；否则要求 `exit_code == expected`）。
3. **第一个闭标记**：`core.py:343-346` `end = next((index for index in range(start+1, len(lines)) if lines[index].strip() == "```"), None)`；`reconcile.py:25` 同构实现。两者都取**第一个**闭标记，证据块正文含其他围栏时不会误判。

## 六、gate 复跑（补齐三份报告后）

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/gate-deletion-semantics-continuation-1 --task-id gate-deletion-semantics-continuation-1
→ status: pass, exit 0, errors: []
```

补记：补齐两份终审文件**之前**，同一命令返回 `blocked / exit 3 / errors: ["missing final-check.md", "missing final-result.json"]`——与前置状态描述一致。

## 七、对执行与审查两阶段的确认

- **执行阶段**：`executor-report.md` + `executor-result.json` 存在、非空、身份正确（task_id / branch / worktree 匹配）。事实核验成立，但**存在报告完整性缺口**（漏报 freshness 失败，见第一节）。
- **审查阶段**：`review-report.md` + `reviewer-result.json` 存在、非空、身份正确，结论 `ACCEPT WITH CONDITIONS`。审查者的两个条件（记录 freshness 失败、上报 `forbidden_paths` 矛盾）本终审均已履行。
- 三份报告均只含**恰好一个** `pipeline-evidence` 块，格式合规。

## 八、无删除日志引用

本报告不引用任何已删除的原始日志（`goal.md:51`：成功最终化后不得引用已删除的原始日志）。所引证据均为当前任务目录内的现存文件。

## 九、未验证项

- `.gitattributes` 的行尾策略需要一次全新 clone 才能端到端验证。
- F1 的两条根因修复本身未实施（不在本任务范围）。
- 第 1/5/6 项扩张（补回的 4 条命令、`.gitattributes`、15 个 `.pipeline/` 文件行尾规范化）按任务单已声明**无既有测试**，仅以提交哈希记录，未被机械核验。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "gate-deletion-semantics-continuation-1",
  "acceptance_id_format": "acceptance-test-*",
  "worktree": ".worktrees/gate-deletion-semantics-continuation-1",
  "branch": "gate-deletion-semantics-continuation-1",
  "role": "main-final",
  "round": 1,
  "status": "PASS",
  "commands": [
    {"command": "git log --oneline -8", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "git show --stat 5bf40a3 && git show --stat 9f0e6cc && git show --stat ba5e8bb", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "git status --short && git status --short --untracked-files=no", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "git diff c92788c HEAD --name-status", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "sha256sum docs/tasks/gate-deletion-semantics-continuation-1.md", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "git diff 5bf40a3 9f0e6cc --name-only", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "git merge-base --is-ancestor 5bf40a3 HEAD", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_evidence.EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_boolean_expected_exit_code", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_evidence.EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/gate-deletion-semantics-continuation-1 --task-id gate-deletion-semantics-continuation-1", "exit_code": 0, "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json lifecycle status . --task-id gate-deletion-semantics-continuation-1 --evidence .pipeline/gate-deletion-semantics-continuation-1", "exit_code": 0, "evidence_ref": "final-check.md"}
  ],
  "assertions": [
    "freshness independently re-run: status blocked, exit 3, errors [product/test HEAD drifted, evidence artifact missing], evidence_only false",
    "freshness root cause A: core.py:1403 resolves acceptance[].evidence_refs against the repository root while core.py:313-325 resolves commands[].evidence_ref against the evidence directory",
    "freshness root cause B: core.py:1391-1393 does not exempt .pipeline/metrics/ although core.py:277-281 treats metrics as workflow metadata",
    "the executor did not report the freshness failure in either executor-report.md or executor-result.json",
    "F2: git diff 5bf40a3 9f0e6cc --name-only lists exactly one file; git merge-base --is-ancestor 5bf40a3 HEAD exits 0",
    "gate_check at core.py:1534 does not call scope_check; its calls are evidence_verify, implement_plan_status, _read_machine_evidence, _machine_result_errors, git diff --check, git ls-files -u, git rev-parse, _post_merge_reverified_in_main_worktree",
    "scope check requires --allowed explicitly (_add_scope_args, __main__.py:76-78)",
    "the evidence_refs fix is out of scope: allowed_paths has 3 entries without pipeline_tools/** and non_goals item 4 forbids modifying pipeline_tools/",
    "all four acceptance tests pass independently with exit code 0",
    "full suite: Ran 275 tests in 200.718s, OK, exit code 0",
    "task sheet sha256 is unchanged at 1721091c5a2d7bb8776cce38e9c7bd9560e6d9f99ed6ca5198d9ca2b839b8129",
    "core.py:252 deleting = status.startswith(D) and core.py:263 if retained == deleting:",
    "expected_exit_code and boolean guards at core.py:435-441 and core.py:1581-1590",
    "first closing fence via next(...) at core.py:343-346 and reconcile.py:25",
    "gate pre-merge returns pass / exit 0 once final-check.md and final-result.json exist"
  ],
  "evidence_refs": ["executor-report.md", "review-report.md", "final-check.md"],
  "unverified": [
    ".gitattributes line-ending effect requires a fresh clone to validate end-to-end",
    "the freshness root-cause fixes are not implemented; out of scope for this task",
    "expansions 1, 5 and 6 have no existing test and are recorded by commit hash only",
    "merge to main and post-merge gate are not performed in this round"
  ],
  "identity": {
    "product_head": "5bf40a3b0971d0a6dbb1ca07aff864f348660f74"
  }
}
```