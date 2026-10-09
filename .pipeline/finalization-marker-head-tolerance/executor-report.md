# executor-report：finalization-marker-head-tolerance

## 任务身份

- task-id：`finalization-marker-head-tolerance`
- task-type：`repair`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\finalization-marker-head-tolerance`
- branch：`finalization-marker-head-tolerance`
- baseline HEAD：`fe72596fb2ba134549f9f269b8844a83bc9d5da0`
- 实现提交：`39c8984b98dee0cd5669d5e670547e777bee794b`
- role：executor，round 2
- sheet_revision：1
- sheet_sha256：`b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76`

## 环境检查（逐项）

| # | 检查 | 结果 |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` == worktree 绝对路径 | PASS（`D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance`） |
| 2 | `git branch --show-current` == `finalization-marker-head-tolerance` | PASS |
| 3 | `python -m pipeline_tools task validate docs/tasks/finalization-marker-head-tolerance.md` | PASS，退出码 0 |
| 4 | `python -m pytest --version` | PASS（pytest 9.1.1） |
| 5 | `<worktree>/.pipeline/finalization-marker-head-tolerance/` 可写 | PASS（目录原先不存在，已 `mkdir -p` 并写入探测文件后删除；本目录是 allowed_paths，非 worktree 创建） |
| 6 | 不建 worktree / 不动主工作树 / 不改其它任务证据目录 | PASS（`git status` 仅出现本任务 allowed_paths；未对 `.pipeline/finalization-and-reconcile-phase/**` 等写入） |

## 缺陷与判据

缺陷：`pipeline_tools/core.py` 的 `verify_finalization_snapshot` 要求标记 `identity.head` **严格等于**当前 HEAD。提交 `finalization.json` 这一动作本身推进 HEAD，于是标记在提交后自我失效——`evidence verify --phase finalized` 报 `finalization head is stale`，循环不可满足。

改动位置：`pipeline_tools/core.py:1166-1193`（`verify_finalization_snapshot`），仅 `head` 分支：

- 新增 `identity_root = root or _evidence_root(directory)`，`current = git_identity(identity_root)`。
- 每个 key 仍先做既有规范化与相等比较，相等即通过。
- `head` 不等且 `head_advanced_by_evidence_only(identity_root, recorded, current.get("head"), directory)` 为真时放行；`branch`、`worktree` **不适用**该容忍，仍严格相等。
- 其余情形照旧追加 `finalization {key} is stale`。`retained_sha256` 快照失配分支未改动。

复用既有辅助函数（`core.py:2706`），因此天然 fail-closed：`head` 非字符串、非 40 位十六进制、`merge-base --is-ancestor` 为假、`git diff` 不可解析、区间内出现非证据路径或证据目录无法相对根解析，一律返回 False → 仍报 stale。

幂等复核：`planning._finalize_evidence_unlocked:2605` 与 CLI `evidence verify`（`__main__.py:1191`）都调用同一函数，故提交标记后重复 `evidence-finalize` 仍返回 `finalized`。

### 决策点 1（branch / worktree）的核查

未触发。`branch`/`worktree` 不存在自指循环——提交标记不会改变分支或 worktree。既有 E2E（`test_finalization_accepts_schema_two_reports`）与新增端到端演示都在主工作树（post-merge 的唯一合法终审现场：`gate post-merge` 硬要求 `final-check.md` 有一条 `cwd` 解析到主工作树根、`exit_code == 0` 的命令）完成最终化，标记记录的 `branch=main`、`worktree=<主工作树根>` 与校验时身份一致。在任务 worktree 内最终化属于流程误用（该现场过不了 post-merge gate），不是判据循环，故未扩围。

## 端到端演示（真实命令与退出码）

脚本临时仓库流程：`git merge --no-ff demo-task` → `gate post-merge` → `planning evidence-finalize` → 提交 `finalization.json` → `verify_finalization_snapshot` → `evidence verify --phase finalized` → 重复 `evidence-finalize`。所有 CLI 命令 `cwd`=临时仓库根，`PYTHONPATH`=本 worktree，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

```
# merge complete: baseline=ae4d0dc8 merged=cebe7e2a
$ python -m pipeline_tools gate post-merge <root>/.pipeline/demo --task-id demo --branch main
  exit_code=0           stdout: PASS
$ python -m pipeline_tools planning evidence-finalize <root>/.pipeline/demo --task-id demo --success
  exit_code=0           stdout: {"status": "finalized", "missing": [], "finalization": "...finalization.json"}
# marker identity head=cebe7e2a branch=main
$ git -C <root> commit -qm "finalization marker"        # 提交标记，HEAD 前移
  exit_code=0
# published=058b88c4 changed_since_marker_head=['.pipeline/demo/finalization.json']
$ python -c "verify_finalization_snapshot(evidence, marker)"
  exit_code=0           stdout: errors= []
$ python -m pipeline_tools evidence verify <root>/.pipeline/demo --task-id demo --phase finalized
  exit_code=0           stdout: PASS
$ python -m pipeline_tools planning evidence-finalize <root>/.pipeline/demo --task-id demo --success
  exit_code=0           stdout: {"status": "finalized", "missing": [], "finalization": "...finalization.json"}
$ python -m pipeline_tools evidence verify <root>/.pipeline/demo --task-id demo --phase finalized
  exit_code=0           stdout: PASS
E2E_SCRIPT_EXIT=0
```

标记 head（`cebe7e2a`）在提交后被 HEAD（`058b88c4`）推进，区间内只有 `.pipeline/demo/finalization.json`；校验通过，重复 `evidence-finalize` 仍 `finalized`。

## 双向实测

### 修复前确实失败（证明用例非空转）

临时 `git stash` 回退 `pipeline_tools/core.py` 后单跑验收测试1：

```
$ python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits
  exit_code=1
  AssertionError: Lists differ: [] != ['finalization head is stale']
  FAILED tests/test_planning.py::PlanningTests::test_finalization_marker_head_survives_evidence_only_commits
```

随后 `git stash pop` 恢复。

### 证据提交后不再 stale

`test_finalization_marker_head_survives_evidence_only_commits` 断言：提交标记后 HEAD 前移且区间恰为 `['.pipeline/demo/finalization.json']`；`verify_finalization_snapshot` 返回 `[]`；CLI `evidence verify --phase finalized` 退出 0；重复 `evidence-finalize` 返回 `finalized`。

### 产品路径改动后仍 stale

`test_finalization_marker_head_is_still_stale_after_product_commits`：先以证据-only 提交发布标记（`verify_finalization_snapshot` 返回 `[]`，证明容忍生效），再提交 `src/app.py` 产品改动 → 仍含 `finalization head is stale`；另将标记 head 改写为非 HEAD 祖先的 `1`*40 → 恰好 `['finalization head is stale']`（fail-closed）。

### 快照失配仍被拒绝

`test_finalization_marker_snapshot_mismatch_is_still_rejected`：发布标记后篡改保留证据 `final-check.md`，`verify_finalization_snapshot` 返回**恰好** `['finalization retained evidence hash mismatch']`（证明容忍未掩盖 retention 判据），`finalize_evidence` 返回 `blocked` 且 `missing` 含该错误。

## 未改动即既有断言的保障

- `retained_sha256` 判据分支、`branch`/`worktree` 判定逻辑逐字未改。
- 既有 `tests/test_planning.py` 断言与其它测试文件断言未删未放宽；全量测试由基线 392 增至 395（+3 新增用例）。
- `tests/test_acceptance_id_and_template_compliance.py` 的既有断言未动；`references/merge-and-recovery.md` 只**新增**一段（新增“最终化标记的 head 判据”），未删改既有行。

## 改动文件清单（仅正文记录）

实现提交 `39c8984b98dee0cd5669d5e670547e777bee794b` 触及的文件：

- `pipeline_tools/core.py` —— `verify_finalization_snapshot` 的 head 判据。
- `tests/test_planning.py` —— 三个新验收用例。
- `references/merge-and-recovery.md` —— 「合并后」小节新增一段。

这些是仓库根相对的产品/文档路径，只在此处正文记录；它们**不**出现在本报告的 `evidence_refs` 或 `commands[].evidence_ref` 中——引用解析规则（`_evidence_file_exists`）把不以 `.pipeline/` 开头的引用按证据目录内相对路径解析，产品路径写进引用会解析失败。

## 本轮修订（round 2）

上一轮独立审查发现：round 1 报告的 `evidence_refs` 混入了 4 条根相对产品路径（`pipeline_tools/core.py`、`tests/test_planning.py`、`references/merge-and-recovery.md`、`docs/tasks/finalization-marker-head-tolerance.md`），按 `_evidence_file_exists` 均不可解析，会让本任务最终化后 `evidence verify --phase finalized` 报 `executor-report.md evidence_ref is missing or not relative`。本轮只改证据：

- `evidence_refs` 收敛为证据目录内真实存在的保留集文件（`.pipeline/finalization-marker-head-tolerance/executor-report.md`、`.pipeline/finalization-marker-head-tolerance/executor-result.json`）。
- 产品/文档路径信息保留在上文正文与小节标题中，不再作为引用。
- `commands[].evidence_ref` 原本已是 `.pipeline/...` 形态，可解析，未改。
- `executor-result.json` 的 `acceptance[].evidence_refs` 原本已是 `.pipeline/...` 形态，可解析，未改。

实现代码未动；round 1 的 `39c8984` 与针对它的审查证据 `e0199a8` 保持不变。

## 文档

`references/merge-and-recovery.md` 的「合并后」小节新增一段（插在第 47 行后），写明：标记 `head` 等于 HEAD 或仅被本任务证据提交推进（复用 `head_advanced_by_evidence_only`，证据目录取该任务证据目录）；产品路径/非证据路径改动、head 非合法提交或非祖先仍报 `finalization head is stale`；`branch`/`worktree` 仍严格相等；`retained_sha256` 失配仍报 hash mismatch；重复 `evidence-finalize` 仍 `finalized`。

## 命令与退出码汇总

见文末 `pipeline-evidence` 区块 `commands` 字段。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "finalization-marker-head-tolerance",
  "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
  "branch": "finalization-marker-head-tolerance",
  "role": "executor",
  "round": 2,
  "status": "PASS",
  "head": "39c8984b98dee0cd5669d5e670547e777bee794b",
  "sheet_revision": 1,
  "sheet_sha256": "b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76",
  "observed_at_commit": "39c8984b98dee0cd5669d5e670547e777bee794b",
  "generated_at": "2026-10-09T00:40:00+00:00",
  "commands": [
    {
      "command": "python -m pipeline_tools task validate docs/tasks/finalization-marker-head-tolerance.md",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_is_still_stale_after_product_commits",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_marker_snapshot_mismatch_is_still_rejected",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "python -m pytest -q",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits  (with pipeline_tools/core.py stashed to baseline)",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 1,
      "expected_exit_code": 1,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "python -m pipeline_tools scope check . --allowed pipeline_tools/core.py tests/test_planning.py references/merge-and-recovery.md docs/tasks/finalization-marker-head-tolerance.md .pipeline/finalization-marker-head-tolerance/** --forbidden docs/goal.md .pipeline/finalization-and-reconcile-phase/** .pipeline/post-merge-evidence-identity/** .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/** .env credentials/**",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "git diff --check",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    },
    {
      "command": "python /tmp/e2e_demo.py  (merge -> gate post-merge -> evidence-finalize -> commit marker -> verify -> repeat finalize, in a temporary repo)",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/executor-report.md"
    }
  ],
  "assertions": [
    "Committing finalization.json advances HEAD past marker.identity.head, and the marker still verifies: verify_finalization_snapshot returns [] and evidence verify --phase finalized exits 0",
    "The evidence-only commit range between the marker head and HEAD contains exactly .pipeline/demo/finalization.json",
    "A repeated planning evidence-finalize after the marker commit still returns {\"status\": \"finalized\"}",
    "A product-path commit after the marker head still reports 'finalization head is stale'",
    "A marker head that is not an ancestor of HEAD is still rejected with 'finalization head is stale'",
    "A tampered retained evidence file still reports 'finalization retained evidence hash mismatch' and blocks evidence-finalize",
    "branch and worktree remain exact-equality checked (unchanged code path)",
    "Reverting only the core.py fix makes acceptance-test-1 fail with 'finalization head is stale', so the new test is not vacuous",
    "Full suite passes: 395 passed, 28 subtests passed (baseline 392 + 3 new tests)"
  ],
  "evidence_refs": [
    ".pipeline/finalization-marker-head-tolerance/executor-report.md",
    ".pipeline/finalization-marker-head-tolerance/executor-result.json"
  ],
  "unverified": [
    "Round 1 evidence_refs contained unresolvable root-relative product paths (pipeline_tools/core.py, tests/test_planning.py, references/merge-and-recovery.md, docs/tasks/finalization-marker-head-tolerance.md); this round records them in prose only and keeps evidence_refs to resolvable evidence-directory files.",
    "How many of the sixteen existing finalization.json markers would now pass was not enumerated (contract unknown-2); no historical evidence directory was read or modified.",
    "No post-merge gate was executed against the real repository; all post-merge runs used temporary repositories."
  ]
}
```
