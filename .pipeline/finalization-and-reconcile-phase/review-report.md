# 审查报告：最终化与对账的阶段感知（round 2）

- 任务：`finalization-and-reconcile-phase`
- 角色：reviewer
- worktree：`D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase`（cwd 一律在此）
- branch：`finalization-and-reconcile-phase`
- 本轮待审实现提交（head）：`eae01331b701eb310d35bbccfd17c994b46e259b`
- 审查时分支尖端：`67fc976a891b6338563f1627f243a213ba87c622`
- 契约：`docs/tasks/finalization-and-reconcile-phase.md`，revision 1（未变；`sha256 = 2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8`）
- 契约基线：`f07b9081d9f379c40fbd0436ffea515408c51733`
- 本轮修复范围：`git diff 9f4fbcc..eae0133 --stat` = 8 个文件，其中产品/文档/测试改动 4 个（`pipeline_tools/reconcile.py`、`SKILL.md`、`references/merge-and-recovery.md`、`tests/test_task_evidence_reconcile.py`），其余 4 个为证据文件（含本 reviewer round 1 报告）。
- 全部结论由本审查子代理亲自复验：自建临时仓库夹具、直接调用库函数 + 猴子补丁回放旧逻辑、逐条运行契约命令；未转述执行子代理的任何结论。

## 0. 结论摘要

**PASS**。round 1 发现的 F1 已被真实修复：`_delivery_is_merged` 现在排除 `HEAD` 当前所在分支，未合并任务在「终审报告记当前分支」的形态下重新施加 active 提交绑定（本轮实测 6 条提交身份错误、`verify: BLOCKED`），而真实已合并交付仍达到 `evidence reconcile` PASS。六条验收测试全部退出码 0；全量 `pytest -q` = `392 passed, 28 subtests passed`，与执行者声明一致；A/C/D 未回退；范围与既有断言完整。仅剩一条低severity 残留观察（detached HEAD 下无"当前分支"可比，见 F1-residual），不产生假 PASS。

## 1. 环境检查（逐项）

| # | 检查 | 实测结果 |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase` ✅ |
| 2 | `git branch --show-current` | `finalization-and-reconcile-phase` ✅ |
| 3 | `git rev-parse HEAD` | `67fc976a891b6338563f1627f243a213ba87c622` ✅ |
| 4 | `git merge-base --is-ancestor eae0133 HEAD` | 退出码 0 ✅ |
| 5 | `python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md` | `PASS`，退出码 0 ✅ |
| 6 | 只读产品代码 / 不建 worktree / 不动主工作树 / 不改两个依赖任务证据目录 | 夹具全在系统临时目录；审查期间 `git status --porcelain` 为空 ✅ |

未进入 BLOCKED。

## 2. 本轮 diff 的实质内容

`pipeline_tools/reconcile.py`：
- 新增 `current_branch = git(root, "branch", "--show-current", redact_output=False)[1].strip()`，候选分支循环里 `if branch == current_branch: continue`；
- docstring 同步说明「当前分支永远不是合并信号」；
- **标记信号逐字未动**（`finalization.json` 的 `task_id` + `status == "finalized"` 检查原样保留）；
- 未改动 `reconcile_task` 的阶段选择调用点。

`SKILL.md:83` 与 `references/merge-and-recovery.md:51` 补入「判断分支时排除 `HEAD` 当前所在分支」及其理由——与实现一致。

`tests/test_task_evidence_reconcile.py`：`test_reconcile_keeps_active_binding_for_an_unmerged_task` 加强——同一未合并交付追加「终审报告记录 `HEAD` 当前分支」的第二种形态，并断言 `status == BLOCKED`、`verify == "BLOCKED"`、`head`/`worktree` 各报 `does not match current Git identity`、`status != "PASS"`。

## 3. 第 3 节 1–6 各条的独立观察

### 1. 未合并 + 终审记当前分支 → 必须不再判为已合并（F1 正面复验）

自建夹具：`git init -b main` → 基线 → `git worktree add -b demo-task` → 任务分支提交产品改动（**不合并**）→ 在仓库根 `.pipeline/demo/` 写三份 schema 2 报告（执行/审查记 `demo-task` + 任务 worktree + `task_head`；终审记 `branch = HEAD 当前分支`（实测 `main`）、`worktree = 仓库根`、命令 `cwd = 仓库根`）+ 三份 schema 1 结果。实测：

```
current branch: main | merge-base --is-ancestor demo-task HEAD rc: 1
_delivery_is_merged -> False
status: BLOCKED | verify: BLOCKED
identity errors: 6 条
  ['executor-report.md head does not match current Git identity',
   'executor-report.md branch does not match current Git identity',
   'executor-report.md worktree does not match current Git identity',
   'review-report.md head does not match current Git identity',
   'review-report.md branch does not match current Git identity',
   'review-report.md worktree does not match current Git identity']
```

round 1 同形态下 `_delivery_is_merged` 返回 `True`、身份错误 0 条——**F1 已修复**。旧实现的对照：见本节第 5 条的猴子补丁回放。

### 2. 真实已合并交付仍必须达到 PASS

- 夹具（任务分支身份的执行/审查报告 + 主工作树身份的终审报告 + 合法 `finalization.json`，任务分支 `--no-ff` 合入）：CLI `evidence reconcile <root> --task-id demo` → 退出码 **0**，`"status": "pass"`、`"verify": "PASS"`、`errors: []`，提交身份错误 0 条（`unverified` 仅列机器结果未记录修订版本）。
- 同夹具把任务分支合入但**不写标记**：`_delivery_is_merged` 仍 `True`（经任务分支祖先判定），`verify: PASS`，唯一错误是 `missing or invalid finalization.json`——fail-closed 未放宽。
- 同一份已合并证据在 `evidence verify --phase active` 下退出码 3 并报 `branch`/`worktree` 与当前 Git 身份不符；`--phase finalized` 退出码 0 `PASS`：阶段分工双向成立。

### 3. 对照：三份报告都记任务分支的未合并形态

自建夹具实测 `status: BLOCKED`、`verify: BLOCKED`、6 条提交身份错误——**未回退**（round 1 该形态即为 5 条/6 条错误，本轮数值差异仅来自终审报告的 head 是否等于 HEAD）。

### 4. 边界

| 边界形态 | 实测 |
|---|---|
| detached HEAD（`git checkout --detach`）+ 终审记 `main` | **无异常**；`git branch --show-current` 返回 `''`，故排除规则不生效，`_delivery_is_merged -> True`、`verify: PASS`、身份错误 0 条，但仍 `status: BLOCKED`（仅 `missing or invalid finalization.json`） |
| 报告记**不存在**的分支名 | `_delivery_is_merged -> False`，`verify: BLOCKED`（active 绑定生效） |
| 报告记**存在但非祖先**的旁支分支 | `_delivery_is_merged -> False`，`verify: BLOCKED`（active 生效） |
| 主工作树就在任务分支上（分支"合并进自身"）、三份报告都记该分支 | `_delivery_is_merged -> False`（当前分支被排除），但报告身份本就等于当前身份 → `verify: PASS`、`errors` 只剩缺标记；无异常、无假 PASS |

### 5. 加强夹具是真实的回归护栏（不只看结论）

用猴子补丁把 `_delivery_is_merged` 换回 round 1（未收窄）的实现，对同一份「未合并 + 终审记当前分支」证据分别运行：

```
[new code (eae0133)] verify: BLOCKED | identity errors: 6
[old (pre-F1-fix)]  verify: PASS    | identity errors: 0
the strengthened test asserts verify == 'BLOCKED' -> would FAIL with the old code: True
```

→ 该加强用例在旧逻辑下会失败，说明它确实断言到两种未合并形态，而不是空断言。

### 6. F2 / F3 保持现状（契约要求不作改动）

- 标记信号未动：`_delivery_is_merged` 的 `finalization.json` 分支与 round 1 逐字相同（diff 可见）；自洽伪造标记在未合并交付上仍能让 `reconcile_task` 判 `PASS`（实测：`all errors: []`，而 `merge-base --is-ancestor demo-task HEAD` 返回 1），即契约 `unknown-2` 接受的信任模型边界保持原样。
- 快照不符的伪造标记仍按 round 1 结论被拦下：`reconcile_task` → `BLOCKED`（`finalization retained evidence hash mismatch`、`finalization head is stale`）；`evidence-finalize --success` → 退出码 3 不产出标记。
- `references/merge-and-recovery.md:47` 的「schema 1 报告仅用于 legacy/unverified 查询」**逐字未改**（本轮 diff 只动了第 49 行）；`SKILL.md` 第 82 行（finalized 身份判据）未改。

## 4. 验收测试逐条（cwd = 实现 worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）

| ID | 命令 | 退出码 | 实测 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports` | 0 | `1 passed, 47 deselected in 6.25s` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports` | 0 | `1 passed, 47 deselected in 0.59s` |
| acceptance-test-3 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery` | 0 | `1 passed, 15 deselected in 4.27s` |
| acceptance-test-4 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task` | 0 | `1 passed, 15 deselected in 5.67s` |
| acceptance-test-5 | `python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors` | 0 | `1 passed, 50 deselected in 3.00s` |
| acceptance-test-6 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | `1 passed, 27 deselected in 0.11s` |

另有：`tests/test_task_evidence_reconcile.py::TaskEvidenceReconcileTests::test_old_head_and_worktree_are_blocked_against_current_git_identity` → `1 passed`，退出码 0。

### 全量测试

| 命令 | 退出码 | 实测 |
|---|---|---|
| `python -m pytest -q`（cwd = 实现 worktree） | 0 | `392 passed, 28 subtests passed in 576.52s (0:09:36)` |

**与执行者声明 `392 passed, 28 subtests passed` 一致**，无差异。

### 工作流命令

| 命令 | 退出码 | 实测 |
|---|---|---|
| `python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md` | 0 | `PASS` |
| `python -m pipeline_tools result verify .pipeline/finalization-and-reconcile-phase/reviewer-result.json --task-id finalization-and-reconcile-phase --role reviewer` | 0 | `PASS` |
| `python -m pipeline_tools scope check . --allowed <allowed_paths 逐项> --forbidden <forbidden_paths 逐项>` | 0 | `PASS` |
| `git diff --check` | 0 | 无输出 |

## 5. 范围与既有断言完整性

- `git diff --name-only f07b908 eae0133` = 12 个文件：8 个产品/文档/测试文件（round 1 的 8 个）+ 4 个证据文件（`.pipeline/finalization-and-reconcile-phase/**`）。全部落在 revision 1 的 `allowed_paths` 内。
- `forbidden_paths` 零改动：用 grep 在 `git diff --name-only f07b908 eae0133` 中匹配 `docs/goal.md`、两个依赖任务单、两个依赖任务证据目录 → **无匹配**（exit 1）。
- 既有断言完整性：`git diff f07b908 eae0133 -- tests/` 的删除行**只有 1 行**——

  ```
  9:-from pipeline_tools.core import evidence_freshness, evidence_verify, gate_check, verify_structured_result
  ```

  即 `tests/test_evidence.py` 的单行 import 被改写为多行 import（round 1 已存在）。`tests/test_planning.py`、`tests/test_task_evidence_reconcile.py` **零删除行**，本轮对 reconcile 用例只有追加（+23 行）。无任何断言被删或弱化。
- 证据目录只含保留集文件名：`executor-report.md`、`executor-result.json`、`review-report.md`、`reviewer-result.json`（无额外日志）。

## 6. Findings

### F1-residual（低，仅记录）

`_delivery_is_merged` 用 `git branch --show-current` 取当前分支；detached HEAD 下该值为空串，排除规则无从生效，于是「报告记的分支尖端是 `HEAD` 祖先」的原有宽判据在无分支状态下仍然成立（实测 `_delivery_is_merged -> True`、`verify: PASS`、身份错误 0 条）。影响有限：`finalization.json` 仍是必需项，reconcile 依旧 `BLOCKED`，不产生假 PASS；且实测无异常。若后续想彻底闭合，可在 detached HEAD 时退回 active 或改用 `git_identity` 的 `head` 作为对照。本轮不作要求。

### 已闭合

- **F1（round 1 提出）**：已由 `eae0133` 修复并经双向复验（未合并→active 绑定生效；已合并→PASS）。加强用例在旧逻辑下会失败，属真实回归护栏。
- F2（伪造自洽标记的信任模型边界）与 F3（`merge-and-recovery.md:47` 的 schema 1 旧表述）按契约要求保持原状，本轮 diff 未触碰。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "finalization-and-reconcile-phase",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase",
  "branch": "finalization-and-reconcile-phase",
  "role": "reviewer",
  "round": 2,
  "status": "PASS",
  "head": "eae01331b701eb310d35bbccfd17c994b46e259b",
  "sheet_revision": 1,
  "sheet_sha256": "2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8",
  "observed_at_commit": "67fc976a891b6338563f1627f243a213ba87c622",
  "generated_at": "2026-10-08T23:25:00+00:00",
  "commands": [
    {"command": "git rev-parse --show-toplevel", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git branch --show-current", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git rev-parse HEAD", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git merge-base --is-ancestor eae01331b701eb310d35bbccfd17c994b46e259b HEAD", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git diff 9f4fbcc..eae0133 --stat", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git diff --name-only f07b908 eae0133", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "git diff f07b908 eae0133 -- tests/ (deletion scan)", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
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
    {"command": "python -m pipeline_tools evidence reconcile <fixture root> --task-id demo (unmerged, final-check records HEAD's branch)", "exit_code": 3, "expected_exit_code": 3, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools evidence reconcile <fixture root> --task-id demo (merged delivery)", "exit_code": 0, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools evidence verify .pipeline/demo --task-id demo --phase active (same merged fixture)", "exit_code": 3, "expected_exit_code": 3, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools evidence verify .pipeline/demo --task-id demo --phase finalized (same merged fixture)", "exit_code": 0, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"},
    {"command": "python -m pipeline_tools planning evidence-finalize .pipeline/demo --task-id demo --success (forged inconsistent marker, unmerged task)", "exit_code": 3, "expected_exit_code": 3, "cwd": "<temporary fixture repository root>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/review-report.md"}
  ],
  "assertions": [
    "the round-2 fix excludes HEAD's current branch from the merged-delivery signal, so an unmerged task whose final check records the current branch keeps the active commit binding (six identity errors, verify BLOCKED)",
    "a genuinely merged delivery reaches evidence reconcile PASS with zero commit-identity errors, and without a marker it is still blocked only by the missing finalization.json",
    "the control shape (all reports record the task branch) is not regressed and still reports commit-identity errors",
    "detached HEAD raises no exception; a report naming a missing or non-ancestor branch still falls back to the active criterion",
    "the strengthened acceptance-test-4 fixture is a real regression guard: with the pre-fix logic replayed via monkeypatch it yields verify PASS and zero identity errors, which would fail the new assertion",
    "the marker signal and the schema 1 sentence in references/merge-and-recovery.md are unchanged, as the contract requires for F2/F3",
    "the changed file set is twelve files, all inside allowed_paths, with zero changes to forbidden_paths",
    "no pre-existing assertion was removed or loosened; the only deletion across tests/ is the single import line rewritten in round 1",
    "the full suite reports 392 passed and 28 subtests passed, matching the executor's claim"
  ],
  "evidence_refs": [
    ".pipeline/finalization-and-reconcile-phase/review-report.md",
    ".pipeline/finalization-and-reconcile-phase/reviewer-result.json"
  ],
  "unverified": [
    "all end-to-end fixtures ran in disposable temporary repositories, so their raw output lives in this report rather than in a tracked artifact",
    "finding F1-residual: in detached HEAD there is no current branch to exclude, so the wider ancestor signal still applies; no exception is raised and no false reconcile PASS is reachable because finalization.json stays mandatory"
  ],
  "blockers": [],
  "recommendation": "PASS: merge implementation commit eae01331b701eb310d35bbccfd17c994b46e259b. F1 is fixed in both directions and guarded by a strengthened test that fails against the old logic; all six acceptance tests and the full suite (392 passed, 28 subtests) are green. No further repair is required; F1-residual is a low-severity note for any future hardening."
}
```
