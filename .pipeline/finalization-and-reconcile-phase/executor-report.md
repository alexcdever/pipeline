# 执行报告：最终化与对账的阶段感知（round 2）

- 任务：`finalization-and-reconcile-phase`
- 角色：executor，round 2（修 round 1 独立审查发现的 F1）
- worktree：`D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase`
- branch：`finalization-and-reconcile-phase`
- round 1 实现提交：`9f4fbcc98d229dc80a9302511fca2608f89a3e23`
- **round 2 实现提交：`eae01331b701eb310d35bbccfd17c994b46e259b`**（baseline 仍为 `f07b9081d9f379c40fbd0436ffea515408c51733`，未回退任何已有提交）

## 1. F1 修复（违反 non_goal[0] 的缺陷）

### 症状（审查给出的最小复现，已确认）

`reconcile.py` 的 `_delivery_is_merged` 原来遍历**报告里出现的所有分支名**判断"已合并"。主工作树终审报告记录 `branch: main`，而运行 reconcile 时 `HEAD` 通常就在 `main` 上，`main` 的尖端必然是 `HEAD` 的祖先——于是未合并任务也被判为已合并，`active` 提交绑定被跳过。实测（本机复现）：

```
root=C:\Users\alexc\AppData\Local\Temp\tmp0cdhvqd9 HEAD branch=main
merge-base --is-ancestor main HEAD      -> 0   (0 = yes)
merge-base --is-ancestor demo-task HEAD -> 1   (1 = not merged)
```

即：任务分支确实未合并（rc=1），但当时被纳入候选的 `main` 返回 0，信号被误触发。这不产生假 PASS（`finalization.json` 仍是必需），但让 `non_goal[0]`「不放宽 active 阶段的提交绑定：未合并任务的报告仍必须绑定当前 head、branch 与 worktree」在该形态下不成立。

### 修复

- 文件：`pipeline_tools/reconcile.py:72` `_delivery_is_merged`；关键行 `reconcile.py:97`（取当前分支）与 `reconcile.py:99`（排除）。
- 改动：把候选分支收窄为「报告记录的分支名中，**排除 `HEAD` 当前所在分支**」——`current_branch = git(root, "branch", "--show-current", redact_output=False)[1].strip()`，遍历时 `if branch == current_branch: continue`。
- 理由：主工作树终审报告记录的就是当前分支，它的尖端对 `HEAD` 恒为祖先，与是否合并无关；排除后只剩任务自己的分支，"已合并"才真正等价于"任务分支尖端是 `HEAD` 的祖先"。
- `status: finalized` 且快照自洽的 `finalization.json` 信号**保留不变**（契约 `unknown-2` 明确接受）。
- 未合并路径完全不受影响：未合并任务的分支尖端严格领先 `HEAD`（或分支引用不存在），无标记，两条信号皆不成立 → 仍走 `active`。
- 文档同步（与实现一致）：`SKILL.md:83`、`references/merge-and-recovery.md:51` 补入「判断分支时排除 `HEAD` 当前所在分支」及其理由。

### 违反的 non_goal 恢复情况

修复后复现场景重新走 `active`，提交绑定重新生效（见第 4 节的 6 条身份错误）。

## 2. 环境检查（round 2 重跑）

| # | 检查 | 结果 |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase` ✅ |
| 2 | `git branch --show-current` | `finalization-and-reconcile-phase` ✅ |
| 3 | `task validate docs/tasks/finalization-and-reconcile-phase.md` | `PASS`，退出码 0 ✅ |
| 4 | `python -m pytest --version` | `pytest 9.1.1`，退出码 0 ✅ |
| 5 | 本任务证据目录可写 | 已写入 `executor-report.md` / `executor-result.json` ✅ |
| 6 | 未新建 worktree、未动主工作树、未改历史任务单/证据与依赖任务证据目录 | 所有命令 cwd 在实现 worktree 内，F1 双向实测在系统临时仓库进行 ✅ |

## 3. F1 双向实测（系统临时仓库，未触碰主工作树与依赖任务证据目录）

两种形态使用同一夹具，唯一差别是任务分支是否真的合并：三份 schema 2 报告 + 三份机器结果，**执行与审查报告记任务分支 `demo-task` 与任务 worktree，终审报告记 `branch = HEAD 当前所在分支`（`main`）、`worktree = 仓库根`、命令 `cwd = 仓库根`**。

| 形态 | 命令（cwd = `<临时仓库根>`） | 退出码 | status / verify | `current Git identity` 错误条数 |
|---|---|---|---|---|
| A：未合并（`merge-base --is-ancestor demo-task HEAD` → **1**） | `python -m pipeline_tools evidence reconcile <root> --task-id demo` | **3** | `BLOCKED` / `BLOCKED` | **6** |
| B：真实已合并（`--no-ff` 合入 `main`，`merge-base --is-ancestor demo-task HEAD` → **0**），另带自洽 `finalization.json` | `python -m pipeline_tools evidence reconcile <root> --task-id demo` | **0** | `PASS` / `PASS` | **0** |

形态 A 实测输出（修复后）：

```
--- A unmerged + final-check records current branch
    cwd=C:\Users\alexc\AppData\Local\Temp\tmpepz_eyp5  current branch=main  merge-base --is-ancestor demo-task HEAD -> 1
    command: python -m pipeline_tools evidence reconcile <root> --task-id demo
    exit_code=3  status=BLOCKED  verify=BLOCKED
    'current Git identity' errors = 6
      - executor-report.md head does not match current Git identity
      - executor-report.md branch does not match current Git identity
      - executor-report.md worktree does not match current Git identity
      - review-report.md head does not match current Git identity
      - review-report.md branch does not match current Git identity
      - review-report.md worktree does not match current Git identity
--- B truly merged delivery
    cwd=C:\Users\alexc\AppData\Local\Temp\tmpv3q14bjq  current branch=main  merge-base --is-ancestor demo-task HEAD -> 0
    command: python -m pipeline_tools evidence reconcile <root> --task-id demo
    exit_code=0  status=PASS  verify=PASS
    'current Git identity' errors = 0
```

对照：round 1（修复前）同一形态 A 会得到 `verify: PASS` 且身份错误 0 条；现在回到 `BLOCKED` + 6 条身份错误，形态 B 不受影响仍为 PASS。两条都覆盖了要求的方向。

## 4. 验收测试逐条（cwd = 实现 worktree，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）

| ID | 命令 | 退出码 | 结果 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports` | 0 | `1 passed, 47 deselected` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports` | 0 | `1 passed, 47 deselected` |
| acceptance-test-3 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery` | 0 | `1 passed, 15 deselected` |
| acceptance-test-4 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task` | 0 | `1 passed, 15 deselected` |
| acceptance-test-5 | `python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors` | 0 | `1 passed, 50 deselected` |
| acceptance-test-6 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | `1 passed, 27 deselected` |

**验收测试 4 已加强**（用例名与类名不变仍为 `tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_keeps_active_binding_for_an_unmerged_task`，`test_task_evidence_reconcile.py:227`）：同一未合并任务上依次构造并断言两种形态——

1. 三份报告都记任务分支 `demo-task`：断言 `status == BLOCKED`、`verify == BLOCKED`，且 `head`/`worktree` 均报「does not match current Git identity」；
2. 终审报告改记 `HEAD` 当前所在分支（`main`）、`worktree = 仓库根`、`head = 当前 HEAD`、命令 `cwd = 仓库根`：断言同样 `BLOCKED`、`verify == BLOCKED`，且两种形态都至少有一条 `current Git identity` 错误（`test_task_evidence_reconcile.py:264` 起为该形态）。

未削弱任何既有断言；`test_old_head_and_worktree_are_blocked_against_current_git_identity` 逐字未动且通过。

### 全量测试

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -m pytest -q`（cwd = 实现 worktree） | 0 | `392 passed, 28 subtests passed in 420.03s` |

与 round 2 基线（392 passed / 28 subtests）一致：本轮只加强既有用例、未新增用例数，28 subtests 不减。

## 5. 工作流检查

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -m pipeline_tools task validate docs/tasks/finalization-and-reconcile-phase.md` | 0 | `PASS` |
| `python -m pipeline_tools result verify .pipeline/finalization-and-reconcile-phase/executor-result.json --task-id finalization-and-reconcile-phase --role executor` | 0 | `PASS` |
| `python -m pipeline_tools scope check . --task-id finalization-and-reconcile-phase --allowed pipeline_tools/core.py pipeline_tools/planning.py pipeline_tools/reconcile.py tests/test_planning.py tests/test_evidence.py tests/test_task_evidence_reconcile.py SKILL.md references/merge-and-recovery.md docs/tasks/finalization-and-reconcile-phase.md ".pipeline/finalization-and-reconcile-phase/**" --forbidden docs/goal.md` | 0 | `PASS` |
| `git diff --check` | 0 | 无输出 |

## 6. 明确未修（按指示保留现状）

- **F2**：自洽的伪造 `finalization.json` 可让 reconcile 对未合并交付判 PASS。契约 `unknown-2` 已把"标记存在"列为可接受信号，属信任模型边界，保留现状。
- **F3**：`references/merge-and-recovery.md:47` 关于 schema 1 的旧表述与"最终化接受 schema 1"字面张力；该句改动前即存在，`gate post-merge` 在 CLI 上仍拒绝 schema 1，行为无冲突，保留现状。

## 7. 证据

本轮只写 `executor-report.md` 与 `executor-result.json` 两个文件，单独一次证据提交；`review-report.md`/`reviewer-result.json` 为审查角色产物，未改动。原始命令输出按保留集规则写在报告正文（第 3、4、5 节）。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "finalization-and-reconcile-phase",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase",
  "branch": "finalization-and-reconcile-phase",
  "role": "executor",
  "round": 2,
  "status": "PASS",
  "head": "eae01331b701eb310d35bbccfd17c994b46e259b",
  "sheet_revision": 1,
  "sheet_sha256": "2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8",
  "observed_at_commit": "eae01331b701eb310d35bbccfd17c994b46e259b",
  "generated_at": "2026-10-08T23:08:44+00:00",
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
    {"command": "python -m pipeline_tools evidence reconcile <temporary repository root> --task-id demo   (unmerged shape, final-check records the current branch)", "exit_code": 3, "expected_exit_code": 3, "cwd": "<temporary repository root, unmerged>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools evidence reconcile <temporary repository root> --task-id demo   (truly merged delivery)", "exit_code": 0, "cwd": "<temporary repository root, merged>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "git merge-base --is-ancestor demo-task HEAD   (unmerged shape)", "exit_code": 1, "expected_exit_code": 1, "cwd": "<temporary repository root, unmerged>", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools result verify .pipeline/finalization-and-reconcile-phase/executor-result.json --task-id finalization-and-reconcile-phase --role executor", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "python -m pipeline_tools scope check . --task-id finalization-and-reconcile-phase --allowed pipeline_tools/core.py pipeline_tools/planning.py pipeline_tools/reconcile.py tests/test_planning.py tests/test_evidence.py tests/test_task_evidence_reconcile.py SKILL.md references/merge-and-recovery.md docs/tasks/finalization-and-reconcile-phase.md .pipeline/finalization-and-reconcile-phase/** --forbidden docs/goal.md", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"},
    {"command": "git diff --check", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-and-reconcile-phase", "evidence_ref": ".pipeline/finalization-and-reconcile-phase/executor-report.md"}
  ],
  "assertions": [
    "the merged-delivery signal now excludes the branch HEAD is on, so a main-worktree final check can no longer make an unmerged task look merged",
    "the unmerged repro shape returns exit code 3, status BLOCKED, verify BLOCKED and 6 commit-identity errors",
    "a truly merged delivery (task branch tip an ancestor of HEAD) still reaches PASS with 0 commit-identity errors",
    "a self-consistent finalized marker remains an accepted merge signal",
    "acceptance-test-4 now covers both unmerged shapes and asserts the commit binding applies in each",
    "all six acceptance tests pass, the full suite is 392 passed with 28 subtests, and no pre-existing assertion was weakened",
    "the pre-existing active-binding test test_old_head_and_worktree_are_blocked_against_current_git_identity is unchanged and passing"
  ],
  "evidence_refs": [
    ".pipeline/finalization-and-reconcile-phase/executor-report.md",
    ".pipeline/finalization-and-reconcile-phase/executor-result.json"
  ],
  "unverified": [
    "round 1 independent review found F1 (the merged-delivery signal was too wide); this round fixes it by excluding HEAD's current branch from the candidate branches",
    "the schema distribution of the sixteen historical finalization markers was not enumerated; acceptance of both schema 1 and schema 2 keeps historical and current evidence working",
    "the F1 bidirectional demonstration ran in disposable temporary repositories, so its raw output lives in this report rather than in a tracked artifact",
    "F2 and F3 are recorded as known boundaries and were deliberately left unchanged"
  ]
}
```
