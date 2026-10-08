# 审查报告：最终化与对账的阶段感知（round 1）

- 任务：`finalization-and-reconcile-phase`
- 角色：reviewer
- worktree：`D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase`（cwd 一律在此）
- branch：`finalization-and-reconcile-phase`
- 待审实现提交：`9f4fbcc98d229dc80a9302511fca2608f89a3e23`
- 审查时分支尖端：`cd0f70428e95cbf19aebc8b6d06460993b874fb3`
- 契约：`docs/tasks/finalization-and-reconcile-phase.md`，revision 1（`sha256 = 2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8`，与执行报告一致）
- 契约基线：`f07b9081d9f379c40fbd0436ffea515408c51733`（任务单冻结提交）
- 全部结论由本审查子代理亲自复验：自建临时仓库夹具、直接调用库函数、逐条运行契约命令；未转述执行子代理的任何结论。

## 0. 结论摘要

**PASS**（6 条验收测试全部退出码 0；全量 `pytest -q` = `392 passed, 28 subtests passed`，与执行者声明一致；A–D 四项修复均按契约生效；无既有断言被删改；范围与禁改路径干净）。发现一处需要跟踪的缺陷 F1（对账「已合并」判据过宽，见第 5 节），它不会造成 reconcile 的假 PASS，但会在一个可构造的未合并形态下静默跳过 active 提交绑定；按契约「判定契约本身有缺陷时单列 findings，不自行改契约」处理。

## 1. 环境检查（逐项）

| # | 检查 | 实测结果 |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase` ✅ |
| 2 | `git branch --show-current` | `finalization-and-reconcile-phase` ✅ |
| 3 | `git rev-parse HEAD` | `cd0f70428e95cbf19aebc8b6d06460993b874fb3` ✅ |
| 4 | `git merge-base --is-ancestor 9f4fbcc HEAD` | 退出码 0 ✅ |
| 5 | `python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md` | `PASS`，退出码 0 ✅ |
| 6 | 只读产品代码 / 不建 worktree / 不动主工作树 / 不改两个依赖任务证据目录 | 全程 cwd 在本 worktree 内，夹具建在系统临时目录；`git status --porcelain` 在审查期间为空 ✅ |

环境前置通过，未进入 BLOCKED。

## 2. 改动范围（对照 `allowed_paths` / `forbidden_paths`）

`git diff --name-only f07b908 9f4fbcc` → 8 个文件，全部落在 revision 1 的 `allowed_paths` 内：

```
SKILL.md
pipeline_tools/core.py
pipeline_tools/planning.py
pipeline_tools/reconcile.py
references/merge-and-recovery.md
tests/test_evidence.py
tests/test_planning.py
tests/test_task_evidence_reconcile.py
```

`git diff --name-only 9f4fbcc cd0f704` → 仅 `.pipeline/finalization-and-reconcile-phase/executor-report.md`、`.pipeline/finalization-and-reconcile-phase/executor-result.json`（本任务证据，属允许路径）。

`forbidden_paths` 零改动：`docs/goal.md`、两个依赖任务单、`.pipeline/task-sheet-revision-and-evidence-binding/**`、`.pipeline/post-merge-evidence-identity/**` 均未出现在任一 diff 中。`docs/tasks/finalization-and-reconcile-phase.md` 未被实现改动（`sheet_revision` 仍为 1，证据目录下无 `amendments.json`）。

`pipeline_tools scope check . --allowed <allowed_paths 逐项> --forbidden <forbidden_paths 逐项>` → `PASS`，退出码 0（工作树无未提交漂移）。

## 3. A–D 的独立复验

### A 最终化接受当前报告 schema

- `pipeline_tools/planning.py:2413 _validate_finalization_report`：`required` 元组逐字未动；新增 `schema not in {1, 2} → False`，`schema == 2` 时额外要求 `head` 匹配 `[0-9a-fA-F]{40}`；其余（角色、`task_id`、`POST_MERGE_REPORT_STATUSES` 状态集合、worktree/branch/round/commands/assertions/evidence_refs/unverified 形状）与改动前一致。
- 直接调用库函数（临时目录里构造三种报告）：

  | 输入 | 期望 | 实测 `_validate_finalization_report` |
  |---|---|---|
  | schema 2 完整 | 接受 | `True` |
  | schema 1（无 `head`/`generated_at`） | 接受 | `True` |
  | schema 2 `head="not-a-hash"` | 拒绝 | `False` |
  | schema 2 无 `head` | 拒绝 | `False` |
  | schema 3 | 拒绝 | `False` |
  | 角色不符 | 拒绝 | `False` |
  | `task_id` 不符 | 拒绝 | `False` |

- **端到端（夹具 1）**：临时仓库 `git init -b main` → 提交基线 → `git worktree add -b demo-task` → 在任务 worktree 写 3 份 schema 2 报告（身份 = 任务分支 `demo-task` + 任务 worktree，`final-check.md` 的复验命令 `cwd` 为主工作树根）+ 3 份 schema 1 机器结果 → 提交证据 → 任务分支加一笔产品改动 → `git merge --no-ff demo-task` → 依次运行：

  | 命令（cwd = 临时仓库根） | 退出码 | 输出 |
  |---|---|---|
  | `gate post-merge .pipeline/demo --task-id demo` | 0 | `PASS`（另有 `UNVERIFIED: goal hash unrecorded`，属未验证项） |
  | `planning evidence-finalize .pipeline/demo --task-id demo --success` | 0 | `{"status": "finalized", …}`，`finalization.json` 已生成，`status: finalized` |
  | `evidence verify .pipeline/demo --task-id demo --phase finalized` | 0 | `PASS` |

  合并后 HEAD=`57c6e937…`，报告记录的 `head`=`5a45f575…`（基线）与任务分支身份均与当前 Git 身份不同——旧行为下三份报告会被判 `invalid`，本次链路全程无提交身份错误。

### A 反方向（必须 blocked）

同一夹具逐项注入后运行 `planning evidence-finalize … --success`：

| 注入 | 退出码 | `status` | `missing` 摘要 | 是否产出 `finalization.json` |
|---|---|---|---|---|
| `executor-report.md` 缺 `assertions` | 3 | `blocked` | `executor-report.md missing field: assertions` | 否 |
| `review-report.md` `role="executor"` | 3 | `blocked` | `review-report.md role mismatch` | 否 |
| `executor-report.md` `task_id="other-task"` | 3 | `blocked` | `executor-report.md task identity mismatch` | 否 |
| schema 2 `head="xyz"` | 3 | `blocked` | `head is not a valid commit` | 否 |
| schema 2 无 `head` | 3 | `blocked` | `head must be a non-empty string` | 否 |
| `status="NOPE"` | 3 | `blocked` | `status is invalid` / `not post-merge passing` | 否 |
| `schema=3` | 3 | `blocked` | `schema must be 1 or 2` | 否 |

- **legacy schema 1 未被丢弃**：三份 schema 1 报告 + 三份结果通过库级 `finalize_evidence(dir, 'demo', True)`（不经 `gate post-merge`）→ `status: finalized`。经 CLI 时 schema 1 仍被 `gate post-merge` 挡下（`gate_check` 的 `schema 1 is legacy/unverified` 判据是改动前就有的，本次 diff 未触碰），因此 CLI 路径下 schema 1 与改动前同样不可最终化——**没有因支持 schema 2 而丢失任何 legacy 能力**。

### B 对账的阶段选择

- 夹具 4（已合并，任务分支身份的执行/审查报告 + 主工作树身份的终审报告，`finalization.json` 合法）：
  - `reconcile_task` → `status: PASS`，`verify: PASS`，`errors: []`，`current Git identity` 错误数 = 0。
  - CLI `evidence reconcile <root> --task-id demo` → 退出码 0，`"status": "pass"`，`"verify": "PASS"`，`errors: []`（`unverified` 仅列出机器结果未记录修订版本）。
- 夹具 5a（未合并，三份报告全部记录任务分支 `demo-task`）：`reconcile_task` → `BLOCKED`，`verify: BLOCKED`，报出 5 条提交身份错误（`executor-report.md`/`review-report.md` 的 head+worktree、`final-check.md` 的 worktree 与当前 Git 身份不符）。
- 既有用例 `tests/test_task_evidence_reconcile.py::TaskEvidenceReconcileTests::test_old_head_and_worktree_are_blocked_against_current_git_identity`：单独运行 `1 passed`，退出码 0；`git diff` 显示该用例所在区间**逐字未改**。
- 同一份合并证据在 `evidence verify --phase active` 下仍退出码 3 并报 `branch`/`worktree` 与当前 Git 身份不符；在 `--phase finalized` 下退出码 0 `PASS` —— 阶段分工双向成立。

### C 文档

逐句核对 `references/merge-and-recovery.md` 的「合并后」小节（第 39–51 行）与 `SKILL.md`（第 82–84、87、100、102 行）：

- 旧话（「按修订版本加被验证路径两条判据判定有效性」）已删除；第 51 行改为「有效性只按修订版本判定……"改动路径"判据在该阶段必然成立，因此不再施加」，并补入 `observed_at_commit` 可选与历史形态不新增错误。
- 第 49 行「证据身份的阶段分工」段落中 `observed_at_commit`「仍必须存在且格式合法」已改为「可选记录事实」，并补入 reconcile 的已合并判据。
- 全文 grep `post-merge` / `改动路径` / `提交绑定` 后逐条阅读：**不存在任何**仍声称 post-merge 施加改动路径判据或提交绑定的表述。第 47 行保留的「`finalization.json` 必须可解析且绑定当前 task；缺失、旧 marker 或身份不一致时 reconcile 不能 PASS」讲的是标记本身，与阶段分工不冲突。
- `SKILL.md` 第 82–84 行为新增/改写，与实现一致（`finalized` 只按 task id + `sheet_revision`，`observed_at_commit` 可选，最终化接受 schema 1/2 且 schema 2 须带合法 `head`）。

### D finalized 阶段对历史形态证据的容忍

- **基线对照（最有力的独立证据）**：用 `git archive f07b908 pipeline_tools/` 取出基线包，对同一个「无 `sheet_revision`、无 `observed_at_commit`」的 schema 2 证据运行 `evidence_verify(…, phase='finalized')`：
  - 基线：`['executor-report.md sheet_revision must be a positive integer', 'executor-report.md observed_at_commit must be a non-empty string', … 每份报告两条]`
  - 本次实现：`[]`
  → 历史形态**零新增错误**，正好是本项修复的目标。
- 携带字段时仍按新判据判定（CLI `evidence verify --phase finalized`）：
  - `sheet_revision=99` → 退出码 3，三份报告各报 `was produced against task sheet revision 99 but the current revision is 1`。
  - `sheet_revision=null` → 退出码 3，`sheet_revision must be a positive integer`（字段存在但不合法仍是错误）。
  - `observed_at_commit=""` → 退出码 3，三份报告各报 `observed_at_commit must be a non-empty string`。
  - 完整 schema 2 对照 → 无这类错误。
- 不含 `sheet_revision` 时 `evidence_revision_status` 只在 `unverified` 中说明「未被修订判据覆盖」（`tests/test_evidence.py` 新增用例断言，且我复跑通过）。

## 4. 高风险点逐条独立观察

1. **A 端到端**：见第 3 节夹具 1。`gate post-merge` 0 → `evidence-finalize --success` 0（`status: finalized`）→ `evidence verify --phase finalized` 0 `PASS`。报告的 `branch`/`worktree` 实测为任务分支与任务 worktree（我从磁盘重读报告确认），未通过改写身份或放宽状态集合达标。
2. **A 反方向**：7 种注入全部 blocked 且不产出标记（第 3 节表）；schema 1 三份报告经库级 `finalize_evidence` 仍 `finalized`。
3. **B 已合并路径**：夹具 4，`reconcile_task` 与 CLI `evidence reconcile` 均 PASS，零提交身份错误。
4. **B 未合并路径**：夹具 5a，仍报 5 条提交身份错误；既有钉住 active 绑定的用例未删改且单独运行通过。
5. **B 对抗性探查（重点）**：三种构造，结果分开记录：
   - (i) 指定探针——手工伪造 `status: finalized` 的 `finalization.json`（`retained_sha256` 与磁盘不符、`identity` 陈旧）放进**未合并**任务证据目录：`reconcile_task` → `BLOCKED`，错误为 `finalization retained evidence hash mismatch`、`finalization head is stale`；**active 绑定没有被绕过**（校验仍 blocked）。同一夹具 `planning evidence-finalize --success` 也 → 退出码 3，`missing = [retained evidence hash mismatch, head/branch/worktree is stale]`，不产出标记。**指定探针结论：未绕过。**
   - (ii) 变体——把伪造标记做成**内部自洽**（`retained_sha256` 等于 `retained_evidence_snapshot`、`identity` 等于 `git_identity`）后放进同一个未合并交付：`reconcile_task` → `PASS`，`errors: []`，且任务分支 `demo-task` 仍不是 `HEAD` 的祖先（`merge-base --is-ancestor` 返回 1）。即：一个自洽的 `finalized` 标记可以让 reconcile 对**未合并**交付判 PASS。契约 `unknown-2` 明确把「finalization 标记存在」列为可接受的已合并信号，故这属于标记信任模型的边界而不是实现偏离；但它是执行报告第 3 节「不存在一个信号说已合并、另一个说不合并的构造」这一论证的**反例**，需主代理知悉。
   - (iii) 见 F1：在没有伪造的前提下，只要某份报告记录的 `branch` 是一个「尖端已是 HEAD 祖先」的分支名（例如主工作树终审报告固定记录的 `main`），`_delivery_is_merged` 就会对未合并任务返回 `True`。
6. **C**：见第 3 节，逐句核对，无残留矛盾表述。
7. **D**：见第 3 节，含与 `f07b908` 的逐条错误对照。
8. **阶段分工未回退**：`--phase active` 对（未合并分支、非祖先 head、非规范 worktree）仍逐条报错——夹具 5a 报 5 条、对同一份已合并证据报 `branch`/`worktree` 不符（`head` 因 `task_head..HEAD` 无路径差异按既有的「仅被本任务证据提交推进」规则通过，属改动前行为）；`--phase finalized` 对同样证据退出码 0、无提交身份错误。
9. **既有断言完整性**：`git diff f07b908 9f4fbcc -- tests/` 的删除行只有 1 行，是 `tests/test_evidence.py` 的单行 import 被换成多行 import（便于引入 `evidence_revision_status`）；`tests/test_planning.py`、`tests/test_task_evidence_reconcile.py` 无任何删除行，全部为追加。三个文件中的既有用例体未被触及。
10. **无越界**：见第 2 节，8 个改动文件全在 `allowed_paths` 内，`forbidden_paths` 零改动，`scope check` 退出码 0。

## 5. Findings

### F1（需跟踪）对账「已合并」判据过宽：主分支名也算作合并证明

- 位置：`pipeline_tools/reconcile.py:92-96`（`_delivery_is_merged` 的分支循环）。
- 机制：循环遍历**报告中出现的所有** `branch` 名；当 `refs/heads/<branch>` 存在且 `git merge-base --is-ancestor <branch> HEAD` 返回 0 即判已合并。主工作树终审报告记录 `branch: "main"` 是正常形态（新增验收测试 3 的夹具正是如此），而 `main` 的尖端恒为 `HEAD` 的祖先，于是**只要终审报告记录 `main`，未合并任务也会被判为已合并**。
- 最小复现（未合并任务，报告全部由自建夹具生成，无任何伪造标记）：

  ```bash
  # /tmp/rev1/run5.py 的 5b 段；等价的纯命令序列：
  git init -q -b main <repo> && git -C <repo> commit -qm baseline
  git -C <repo> worktree add -b demo-task <repo>/.worktrees/demo <baseline>
  # 在任务分支提交一笔产品改动；不 merge
  # 在 <repo>/.pipeline/demo/ 写入三份 schema 2 报告 + 三份 schema 1 结果：
  #   executor/review 报告 branch=demo-task、worktree=<repo>/.worktrees/demo、head=<task_head>
  #   final-check.md   branch=main、worktree=<repo>、head=<HEAD>、命令 cwd=<repo>
  python -m pipeline_tools evidence reconcile <repo> --task-id demo
  ```

  实测：`_delivery_is_merged` → `True`（`merge-base --is-ancestor demo-task HEAD` 返回 1，任务确实未合并）；`reconcile_task` → `status: BLOCKED`、`verify: PASS`、提交身份错误 **0 条**，唯一错误是 `missing or invalid finalization.json`。对照组 5a（三份报告都记录 `demo-task`）报出 5 条提交身份错误。
- 影响：reconcile 不会因此产生假 PASS（`finalization.json` 仍是必需项），但 `non_goals[0]`「不放宽 active 阶段的提交绑定」与验收测试 4 的意图在这个形态下不成立，且执行报告第 3 节「未合并任务两条信号皆不成立」的论证给出反例。
- 建议（不在本次实现范围内，交主代理裁决）：只把「候选任务分支」纳入祖先判定——例如排除当前 `HEAD` 所在分支、或只接受与受验 `task_id` 关联的分支名——并补一条「未合并 + 终审报告记录主分支」的用例。
- 判定：契约未规定该判据的具体实现（`chain.application` 只说「阶段选择」），而 `SKILL.md:83` 已把现行判据如实记录，故本条列为 findings，不据此改契约、不判 FAIL。

### F2（记录）执行报告的「两信号不会分歧」论证不成立

`finalization.json` 若被写成内部自洽（哈希与身份都对），reconcile 会对未合并交付判 PASS（第 4 节第 5(ii) 条）。契约 `unknown-2` 把标记列为可接受信号，因此这是标记信任模型的固有边界；执行报告第 3 节「不存在『一个信号说已合并、另一个信号说未合并』的构造」的说法应至少限定为「非伪造标记」。

### F3（低）文档措辞的轻微张力

`references/merge-and-recovery.md:47` 保留的「schema 1 报告仅用于 legacy/unverified 查询」是改动前就有的句子，与本次新增的「最终化接受 schema 1」在字面上略有张力；因 CLI 路径上 `gate post-merge` 仍拒绝 schema 1，实际行为无冲突。本次未要求改，仅记录。

## 6. 验收测试逐条（cwd = 实现 worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）

| ID | 命令 | 退出码 | 实测 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports` | 0 | `1 passed, 47 deselected in 4.06s` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports` | 0 | `1 passed, 47 deselected in 0.40s` |
| acceptance-test-3 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery` | 0 | `1 passed, 15 deselected in 2.97s` |
| acceptance-test-4 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task` | 0 | `1 passed, 15 deselected in 2.63s` |
| acceptance-test-5 | `python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors` | 0 | `1 passed, 50 deselected in 1.81s` |
| acceptance-test-6 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | `1 passed, 27 deselected in 0.05s` |

### 全量测试

| 命令 | 退出码 | 实测 |
|---|---|---|
| `python -m pytest -q`（cwd = 实现 worktree） | 0 | `392 passed, 28 subtests passed in 394.02s (0:06:34)` |

**与执行者声明的 `392 passed, 28 subtests passed` 完全一致**，无差异。

### 工作流命令

| 命令 | 退出码 | 实测 |
|---|---|---|
| `python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md` | 0 | `PASS` |
| `python -m pipeline_tools result verify .pipeline/finalization-and-reconcile-phase/reviewer-result.json --task-id finalization-and-reconcile-phase --role reviewer` | 0 | `PASS` |
| `python -m pipeline_tools scope check . --allowed <allowed_paths 逐项> --forbidden <forbidden_paths 逐项>` | 0 | `PASS` |
| `git diff --check` | 0 | 无输出 |

## 7. 原始观察（夹具脚本不在仓库内）

夹具脚本与运行脚本写在系统临时目录 `C:\Users\alexc\AppData\Local\Temp\rev1\`（`fixture.py`、`run1.py`–`run7.py`），按证据保留集规则不进入 Git；其命令与输出摘要已逐条抄录在第 3、4 节。全部夹具仓库均为 `tempfile` 级临时目录，未触碰主工作树、未新建 worktree、未改动任何产品/测试/文档文件。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "finalization-and-reconcile-phase",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase",
  "branch": "finalization-and-reconcile-phase",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "head": "9f4fbcc98d229dc80a9302511fca2608f89a3e23",
  "sheet_revision": 1,
  "sheet_sha256": "2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8",
  "observed_at_commit": "cd0f70428e95cbf19aebc8b6d06460993b874fb3",
  "generated_at": "2026-10-08T23:05:00+00:00",
  "commands": [
    {"command": "git rev-parse --show-toplevel", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git branch --show-current", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git rev-parse HEAD", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git merge-base --is-ancestor 9f4fbcc98d229dc80a9302511fca2608f89a3e23 HEAD", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py::TaskEvidenceReconcileTests::test_old_head_and_worktree_are_blocked_against_current_git_identity", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pytest -q", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools scope check . --allowed <allowed_paths> --forbidden <forbidden_paths>", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git diff --check", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git diff --name-only f07b9081d9f379c40fbd0436ffea515408c51733 9f4fbcc98d229dc80a9302511fca2608f89a3e23", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git diff f07b9081d9f379c40fbd0436ffea515408c51733 9f4fbcc98d229dc80a9302511fca2608f89a3e23 -- tests/ (deletion scan)", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools gate post-merge .pipeline/demo --task-id demo (fixture repo, merged)", "exit_code": 0, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools planning evidence-finalize .pipeline/demo --task-id demo --success (fixture repo, merged)", "exit_code": 0, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools evidence verify .pipeline/demo --task-id demo --phase finalized (fixture repo, merged)", "exit_code": 0, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools evidence verify .pipeline/demo --task-id demo --phase active (same merged fixture)", "exit_code": 3, "expected_exit_code": 3, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools evidence reconcile <fixture root> --task-id demo (merged delivery)", "exit_code": 0, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools planning evidence-finalize (7 tampered / insufficient report variants)", "exit_code": 3, "expected_exit_code": 3, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools planning evidence-finalize --success (forged inconsistent finalization marker, unmerged task)", "exit_code": 3, "expected_exit_code": 3, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools evidence reconcile <fixture root> --task-id demo (forged inconsistent finalization marker, unmerged task)", "exit_code": 3, "expected_exit_code": 3, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"}
  ],
  "assertions": [
    "finalization accepts both schema 1 and schema 2 reports, and a schema 2 report must still carry a valid 40-hex head",
    "a complete schema 2 delivery with task-branch report identity reaches finalized through the CLI after merging and then passes evidence verify --phase finalized",
    "missing required fields, role mismatch and task_id mismatch all keep finalization blocked and produce no marker",
    "a merged delivery reaches PASS in evidence reconcile with zero commit-identity errors although branch, worktree and head disagree between task-branch reports and the main-worktree final check",
    "an unmerged task whose reports record the task branch still reports head and worktree against the current Git identity, and the pre-existing active-binding test is unchanged and passing",
    "historical-shape schema 2 evidence with neither sheet_revision nor observed_at_commit gains zero new errors in the finalized phase compared with baseline f07b908, while evidence carrying the fields is still judged by them",
    "the stale post-merge changed-path claim is gone from references/merge-and-recovery.md and SKILL.md matches the implementation",
    "the changed file set is eight files, all inside allowed_paths, with zero changes to forbidden_paths",
    "no pre-existing test assertion was removed or loosened; only the test_evidence.py import line was rewritten",
    "the full suite reports 392 passed and 28 subtests passed, matching the executor's claim"
  ],
  "evidence_refs": [
    ".pipeline/finalization-and-reconcile-phase/review-report.md",
    ".pipeline/finalization-and-reconcile-phase/reviewer-result.json"
  ],
  "unverified": [
    "the schema distribution of the sixteen historical finalization markers was not enumerated; accepting both schemas keeps historical and current evidence working",
    "all end-to-end fixtures ran in disposable temporary repositories, so their raw output lives in this report rather than in a tracked artifact",
    "finding F1: an unmerged delivery whose final-check reports branch 'main' loses the active commit binding because _delivery_is_merged accepts any report branch whose tip is an ancestor of HEAD; reconcile still cannot PASS without finalization.json, but the loosening is reachable without forgery"
  ],
  "blockers": [],
  "recommendation": "PASS: merge the implementation commit. The four repairs behave as the contract requires and all six acceptance tests plus the full suite are green. Track F1 (narrow _delivery_is_merged to task branches rather than any branch named by a report, e.g. by excluding the branch HEAD is on) as a follow-up; it cannot produce a false reconcile PASS because finalization.json is still mandatory."
}
```
