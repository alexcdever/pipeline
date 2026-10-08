# 执行报告：最终化与对账的阶段感知（round 1）

- 任务：`finalization-and-reconcile-phase`
- 角色：executor
- worktree：`D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase`
- branch：`finalization-and-reconcile-phase`
- 实现提交：`9f4fbcc98d229dc80a9302511fca2608f89a3e23`（baseline `f07b9081d9f379c40fbd0436ffea515408c51733`）

## 1. 开工前环境检查（逐项）

| # | 检查 | 结果 |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase` ✅ |
| 2 | `git branch --show-current` | `finalization-and-reconcile-phase` ✅ |
| 3 | `python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md` | `PASS`，退出码 0 ✅ |
| 4 | `python -m pytest --version` | `pytest 9.1.1`，退出码 0 ✅ |
| 5 | `.pipeline/finalization-and-reconcile-phase/` 可写 | 创建目录并写入探针文件成功 ✅ |
| 6 | 未运行 `git worktree add`，未建第二个 worktree，未修改主工作树 | 全部命令 cwd 均在实现 worktree 内，E2E 演示在系统临时仓库进行 ✅ |

## 2. A–D 的改动位置与判据

### A（硬阻塞）最终化的报告校验接受当前报告 schema

- 文件：`pipeline_tools/planning.py:2413`（`_validate_finalization_report`）。
- 改动：把原来的 `value.get("schema") == 1` 换为「`schema` 必须属于 `{1, 2}`」；当 `schema == 2` 时额外要求 `head` 存在且匹配 `[0-9a-fA-F]{40}`。
- 保持不变：其余必需字段（`schema`、`task_id`、`worktree`、`branch`、`round`、`status`、`commands`、`assertions`、`evidence_refs`、`unverified`）、角色、`task_id`、以及 `POST_MERGE_REPORT_STATUSES` 状态集合的校验逐条未动。
- 判据说明：schema 1 是历史形态，schema 2 是当前模板产出的形态；两者都必须继续被接受（契约 `unknown-1`）。因此对两种 schema 都接受，而不是拒绝其一——契约 `unknown-1` 明确要求两种都接受，故未触及决策点 1。

### B 对账按交付是否已合并选择阶段判据

- 文件：`pipeline_tools/reconcile.py:72`（新增 `_delivery_is_merged`）、`pipeline_tools/reconcile.py:184`（阶段选择），并在 `reconcile.py:11` 的 `from .core import (...)` 中新增 `git`。
- 改动：`verify_errors = evidence_verify(evidence, task_id, identity.get("branch"), phase)`，其中 `phase` 为 `"finalized"` 当交付已合并，否则 `"active"`。
- 未合并路径逐字不变：`active` 阶段仍以 `identity.get("branch")` 为期望分支，仍逐条报出 `head`/`branch`/`worktree` 与当前 Git 身份不符的错误。
- 既有用例 `tests/test_task_evidence_reconcile.py::TaskEvidenceReconcileTests.test_old_head_and_worktree_are_blocked_against_current_git_identity` **未做任何删改**，继续通过（其交付既无 `finalization.json`，记录的 `demo-branch` 也不存在于仓库，两条信号都不成立）。

### C 删除 `references/merge-and-recovery.md` 中与阶段分工矛盾的旧话

- 文件：`references/merge-and-recovery.md:51`（"合并后"小节末句）。
- 旧话（矛盾原文）：「post-merge 复验证据同样写明它评判的 `sheet_revision`、`sheet_sha256` 与 `observed_at_commit`，并按**修订版本加被验证路径两条判据**判定有效性。」——与本小节上文新写入的阶段分工段落（post-merge 不做提交相对判定）直接冲突。
- 改写为：「有效性只按修订版本判定……"改动路径"判据在该阶段必然成立，因此不再施加。`observed_at_commit` 是可选记录事实，写明即有格式要求，缺失不算错误；不含 `sheet_revision` 的历史形态证据不因此新增错误，只报为 `unverified`。」
- 同时把该小节"证据身份的阶段分工"段落里 `observed_at_commit`「仍必须存在且格式合法」修正为「可选记录事实」，并补入 `reconcile` 的已合并判据，使整节自洽。
- `SKILL.md`：第 82 行改为「`finalized` 阶段仍要求 `head`/`branch`/`worktree` 存在且格式合法，`observed_at_commit` 则是可选记录事实」，fail-closed 段落改为「`sheet_revision` 字段存在但不合法或与当前修订不符时报错，字段缺失则按历史形态处理（不新增错误，只报 `unverified`）」；新增两条记录 reconcile 的已合并判据与最终化接受 schema 1/2（`SKILL.md:83-84`）。

### D finalized 阶段对历史形态证据的容忍

- 文件：`pipeline_tools/core.py:611-628`（`evidence_verify` 的 `finalized` 分支）。
- 改动：
  - `sheet_revision` 只在字段**存在**时判定：`if "sheet_revision" in value:` —— 字段缺失不再计为错误（历史形态），字段存在但不是正整数（含 `null`）仍报 `sheet_revision must be a positive integer`，存在且不等于当前修订仍报版本不符。
  - `observed_at_commit` 由必需改为可选：`observed_at = value.get("observed_at_commit")`，仅当 `observed_at is not None` 时才要求为非空字符串。
  - `branch` 仍必须为非空字符串（未放宽）。
- `evidence_verify` 的 docstring（`core.py:499-514`）同步更新，使文档与实现一致。
- 未退化上一任务钉住的约束：不含 `sheet_revision` 的证据在 finalized 阶段不新增任何错误，只在 `evidence_revision_status` 的 `unverified` 中说明「未被修订判据覆盖」。既有用例 `test_post_merge_rejects_revision_mismatch`（显式写入 `sheet_revision: None` 仍报错）继续通过，未删改。

## 3. B 里「已合并」的机械依据

判据（`_delivery_is_merged`，`pipeline_tools/reconcile.py:72`）：

> 交付已合并 ⇔ 该证据目录存在 `finalization.json`（`task_id` 与受验任务一致且 `status == "finalized"`）**或**报告中记录的分支名在仓库中解析到 `refs/heads/<branch>`，且该分支尖端已是当前 `HEAD` 的祖先。

**两种候选依据为什么不会分歧**（契约 `unknown-2` / 决策点 2）：

- 两个信号各自都是「已合并」的**阳性证明**：`finalized` 标记只在 post-merge 序列（`gate post-merge` → `finalization` → `finalized verify`）走完后写出；分支尖端是 `HEAD` 祖先按定义就是已合并。
- 第二个信号**无法给出阴性结论**：分支引用因合并后被删除而不存在、或分支存在但尖端尚未进入 `HEAD`，只是「缺少第二个证明」，并不等于声明「未合并」。因此不存在「一个信号说已合并、另一个信号说未合并」的构造。
- 取并集（任一成立即算已合并）不会削弱未合并路径：未合并任务的 `finalization.json` 不存在，且其分支尖端严格领先于 `HEAD`、不是祖先，两条信号皆不成立，仍按 `active` 施加完整提交绑定（见验收测试4）。
- 唯一可能同时出现的组合是「标记存在、分支引用已消失」。此时标记本身就是上一次 post-merge 流程的机械记录，语义上该交付确实已进入 post-merge 阶段，判为已合并与阶段分工一致。

## 4. 端到端演示（临时仓库，未触碰主工作树与依赖任务证据目录）

在系统临时仓库（`mktemp -d`，实际路径 `C:\Users\alexc\AppData\Local\Temp\tmp.i6Aoa3qmsw`）执行完整链路：完整 schema 2 证据（三报告 + 三机器结果，执行/审查报告身份为任务分支 `e2e-demo-task` + 任务 worktree，`final-check.md` 的复验命令 `cwd` 为主工作树根）→ 提交证据并在任务分支加一笔产品改动 → `git merge --no-ff` 合入 `main` → 依次运行：

| 命令（cwd = 临时仓库根） | 退出码 | 输出摘要 |
|---|---|---|
| `python -m pipeline_tools gate post-merge .pipeline/e2e-demo --task-id e2e-demo --branch main` | 0 | `PASS`（另有一行 `UNVERIFIED: implement-plan hash unrecorded …`，属未验证项而非错误） |
| `python -m pipeline_tools planning evidence-finalize .pipeline/e2e-demo --task-id e2e-demo --success` | 0 | `{"status": "finalized", "missing": [], "finalization": ".pipeline\\e2e-demo\\finalization.json"}` |
| `python -m pipeline_tools evidence verify .pipeline/e2e-demo --task-id e2e-demo --phase finalized` | 0 | `PASS` |
| `python -m pipeline_tools evidence reconcile <临时仓库根> --task-id e2e-demo` | 0 | `"status": "PASS"`，`"verify": "PASS"`，`"errors": []`；identity 记录 `head`/`branch`/`worktree` 三个字段分歧但不再计入错误 |

关键观测：合并后 `HEAD` = `87d03ec178ea6906dff792267648f695922c5d5b`，报告记录的 `head` = `e5cd22b34126b197261e36ade897517e67d824ec`（任务分支证据提交），二者不同；`finalization.json` 记录的主工作树身份为 `branch: main`，报告记录的是 `e2e-demo-task`。旧行为下这些差异都会累积为提交身份错误，本次一并消失。

演示脚本（原始输出见本节表格与上一段；脚本自身不进入 Git，按证据保留集规则未跟踪）：

```bash
# 结构：init -b main -> 基线提交 -> worktree add -b e2e-demo-task -> 在任务 worktree 写 6 份 schema 2 证据
#      -> 提交证据 -> 任务分支产品改动 -> merge --no-ff -> gate/finalize/verify/reconcile
```

## 5. 验收测试逐条

全部 cwd = 实现 worktree 根，环境变量 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

| ID | 命令 | 退出码 | 结果 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports` | 0 | `1 passed, 47 deselected` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports` | 0 | `1 passed, 47 deselected` |
| acceptance-test-3 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery` | 0 | `1 passed, 15 deselected` |
| acceptance-test-4 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task` | 0 | `1 passed, 15 deselected` |
| acceptance-test-5 | `python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors` | 0 | `1 passed, 50 deselected` |
| acceptance-test-6 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | `1 passed, 27 deselected` |

新增用例落点：

- `tests/test_planning.py: PlanningTests.test_finalization_accepts_schema_two_reports`（集成、端到端：任务 worktree 写 schema 2 证据 → 提交 → 合并 → `planning evidence-finalize` CLI → `evidence verify --phase finalized` 的 CLI，全部退出码 0 并产出 `finalization.json`）。
- `tests/test_planning.py: PlanningTests.test_finalization_still_rejects_incomplete_reports`（先证明完整 schema 2 证据可 finalize，再分别构造缺必需字段 / 角色不符 / `task_id` 不符三种情形，均 blocked、均不产出标记）。
- `tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_reaches_pass_for_a_merged_delivery`（任务分支身份的执行与审查报告 + 主工作树身份的终审报告，合并后 `reconcile_task` 达到 PASS 且无 `current Git identity` 错误）。
- `tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_keeps_active_binding_for_an_unmerged_task`（分支真实存在但未合并，仍报 `head`/`worktree` 与当前 Git 身份不符）。
- `tests/test_evidence.py: EvidenceTests.test_legacy_evidence_gains_no_new_finalized_errors`（无 `sheet_revision`/`observed_at_commit` 的历史形态在 finalized 下零错误，只在 `unverified` 说明；携带字段时仍按新判据判定，含 `sheet_revision: null` 仍报错、`observed_at_commit: ""` 仍报错）。

### 全量测试

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -m pytest -q`（cwd = 实现 worktree） | 0 | `392 passed, 28 subtests passed in 446.15s` |

基线为 387 passed + 28 subtests；新增 5 个用例（验收测试6 为既有用例，不计新增），28 subtests 保持不减。**未删除或放宽任何既有断言**。

### 工作流检查

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md` | 0 | `PASS` |
| `python -m pipeline_tools result verify .pipeline/finalization-and-reconcile-phase/executor-result.json --task-id finalization-and-reconcile-phase --role executor` | 0 | `PASS` |
| `python -m pipeline_tools scope check . --task-id finalization-and-reconcile-phase --allowed <契约 allowed_paths 逐项> --forbidden docs/goal.md` | 0 | `PASS`（变更路径仅本任务 single 允许集，见下方命令块） |
| `git diff --check` | 0 | 无输出 |

提交：实现提交 `9f4fbcc98d229dc80a9302511fca2608f89a3e23`；证据提交见 `git log`（在实现提交之后单独提交）。

## 6. 证据保留集

本轮不产出 `final-check.md`，证据目录当前保留：`executor-report.md`、`executor-result.json`。二者的原始命令输出按保留集规则写在报告正文（见第 4、5 节），未跟踪额外日志文件。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "finalization-and-reconcile-phase",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase",
  "branch": "finalization-and-reconcile-phase",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "head": "9f4fbcc98d229dc80a9302511fca2608f89a3e23",
  "sheet_revision": 1,
  "sheet_sha256": "2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8",
  "observed_at_commit": "9f4fbcc98d229dc80a9302511fca2608f89a3e23",
  "generated_at": "2026-10-08T21:24:00+00:00",
  "commands": [
    {"command": "git -C <worktree> rev-parse --show-toplevel", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "git -C <worktree> branch --show-current", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pytest --version", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pytest -q", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools gate post-merge .pipeline/e2e-demo --task-id e2e-demo --branch main", "exit_code": 0, "cwd": "<temporary repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools planning evidence-finalize .pipeline/e2e-demo --task-id e2e-demo --success", "exit_code": 0, "cwd": "<temporary repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools evidence verify .pipeline/e2e-demo --task-id e2e-demo --phase finalized", "exit_code": 0, "cwd": "<temporary repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools evidence reconcile <temporary repository root> --task-id e2e-demo", "exit_code": 0, "cwd": "<temporary repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools result verify .pipeline/finalization-and-reconcile-phase/executor-result.json --task-id finalization-and-reconcile-phase --role executor", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools scope check . --task-id finalization-and-reconcile-phase --allowed pipeline_tools/core.py pipeline_tools/planning.py pipeline_tools/reconcile.py tests/test_planning.py tests/test_evidence.py tests/test_task_evidence_reconcile.py SKILL.md references/merge-and-recovery.md docs/tasks/finalization-and-reconcile-phase.md .pipeline/finalization-and-reconcile-phase/** --forbidden docs/goal.md", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "git diff --check", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"}
  ],
  "assertions": [
    "finalization accepts both schema 1 and schema 2 reports; a schema 2 report must still carry a valid head",
    "a complete schema 2 delivery that was merged reaches finalized through the CLI and then passes evidence verify --phase finalized",
    "incomplete, role-mismatched and task_id-mismatched reports are still blocked and produce no marker",
    "a merged delivery reaches PASS in evidence reconcile with no commit-identity errors even though branch, worktree and head disagree between the task-branch reports and the main-worktree final check",
    "an unmerged task still reports head and worktree against the current Git identity, and the pre-existing active-binding test is unchanged and passing",
    "historical-shape schema 2 evidence with no sheet_revision and no observed_at_commit gains zero new errors in the finalized phase, while evidence that carries the fields is still judged by them",
    "the stale post-merge changed-path claim is gone from references/merge-and-recovery.md and SKILL.md matches the implementation",
    "no pre-existing assertion was removed or loosened; 387 baseline tests plus 5 new tests all pass"
  ],
  "evidence_refs": [
    ".pipeline/finalization-and-reconcile-phase/executor-report.md",
    ".pipeline/finalization-and-reconcile-phase/executor-result.json"
  ],
  "unverified": [
    "the schema distribution of the sixteen historical finalization markers was not enumerated; acceptance of both schema 1 and schema 2 keeps historical and current evidence working",
    "the end-to-end demonstration ran in a disposable temporary repository, so its raw command output lives in this report rather than in a tracked artifact"
  ]
}
```
