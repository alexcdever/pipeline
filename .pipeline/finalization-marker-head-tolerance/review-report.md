# review-report：finalization-marker-head-tolerance（round 1）

## 审查身份

- task-id：`finalization-marker-head-tolerance`
- 待审实现提交：`39c8984b98dee0cd5669d5e670547e777bee794b`
- 契约基线：`fe72596fb2ba134549f9f269b8844a83bc9d5da0`
- 分支尖端（审查现场）：`c67734009870e4886a606efc8a52d47e219fcd88`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\finalization-marker-head-tolerance`
- branch：`finalization-marker-head-tolerance`
- role：reviewer，round 1
- sheet_revision：1
- sheet_sha256：`b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76`
- 结论：**PASS**

本报告全部结论来自审查子代理在本 worktree 内亲自运行的命令与自建夹具，未转述执行者的任何结论。

## 环境检查（逐项）

| # | 检查 | 结果 |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` == worktree 绝对路径 | PASS（`D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance`） |
| 2 | `git branch --show-current` == `finalization-marker-head-tolerance` | PASS |
| 3 | `git rev-parse HEAD` == `c67734009870e4886a606efc8a52d47e219fcd88` | PASS |
| 4 | `git merge-base --is-ancestor 39c8984 HEAD` 退出码 0 | PASS（exit 0） |
| 5 | `python -m pipeline_tools task validate docs/tasks/finalization-marker-head-tolerance.md` 退出码 0 | PASS（exit 0，stdout `PASS`） |
| 6 | 只读产品代码；临时改动按字节还原；不新建 worktree；不动主工作树；不改其它任务证据目录 | PASS（见下） |

第 6 项的落实证据：

- 唯一一次临时改动是 `pipeline_tools/core.py` 的“修复前回退”实验（第 4 节高风险点 2）。实验前备份字节、实验后 `cp` 还原，`sha256sum` 还原值与 `git show HEAD:pipeline_tools/core.py` 一致（`8fbcde9f…`），`git status --porcelain` 为空。
- 所有临时仓库均建在系统临时目录（`C:\Users\alexc\AppData\Local\Temp\…`），不在仓库内、不新建 worktree。
- 未对主工作树执行任何写操作。
- 未读写、未改动 `.pipeline/finalization-and-reconcile-phase/**`、`.pipeline/post-merge-evidence-identity/**`、`.pipeline/task-sheet-revision-and-evidence-binding/**`、两个 security-scan 证据目录及任何历史证据。

## 本任务修的缺陷（复核）

`pipeline_tools/core.py` 的 `verify_finalization_snapshot`（`pipeline_tools/core.py:1166`）原先对 `identity` 的 `head`/`branch`/`worktree` 一律要求严格等于当前 Git 身份。提交 `finalization.json` 这一动作本身推进 HEAD，于是 `head` 判据循环不可满足，已合并且闸门 PASS 的交付在提交标记后 `evidence verify --phase finalized` 报 `finalization head is stale`。

实现改动仅一处、只影响 `head` 分支：

```python
identity_root = root or _evidence_root(directory)
current = git_identity(identity_root)
for key in ("head", "branch", "worktree"):
    ...
    if recorded == current.get(key):
        continue
    if key == "head" and head_advanced_by_evidence_only(
        identity_root, recorded, current.get("head"), directory
    ):
        continue
    errors.append(f"finalization {key} is stale")
```

`branch`/`worktree` 仍严格相等；`retained_sha256` 判据分支逐字未改。复用既有 `head_advanced_by_evidence_only`（`pipeline_tools/core.py:2716`），其内部 fail-closed：非字符串、非 40 位十六进制、`merge-base --is-ancestor` 为假、`git diff` 不可解析、区间含非证据路径、证据目录无法相对根解析，一律返回 False。

## 高风险点 1–8：独立观察

### 1. 端到端（自建夹具，不依赖本任务测试助手）

我自写脚本 `C:\Users\alexc\AppData\Local\Temp\rev_finalization_check.py`（仓库外临时文件），在系统临时目录新建独立 git 仓库（task id `rev-demo`，与执行者使用的 `demo` 不同，证据内容亦为自撰），驱动真实 CLI 走完整链：schema 2 证据 → 任务分支提交 → 合并（`--no-ff`）→ `gate post-merge` → `planning evidence-finalize` → 提交 `finalization.json` → `verify_finalization_snapshot` → `evidence verify --phase finalized` → 重复 `evidence-finalize`。

观察（两次独立运行一致，下列为第二次的干净结果）：

- `gate post-merge` 退出码 0，stdout `PASS`。
- `evidence-finalize` 退出码 0，`{"status": "finalized", ...}`；标记 `identity.head == 合并后 HEAD`（相等判定 true）。
- 提交标记后 `head_moved = true`，`merged..HEAD` 区间路径恰为 `['.pipeline/rev-demo/finalization.json']`。
- **`verify_finalization_snapshot(evidence, marker)` 返回 `[]`**。
- **`evidence verify --phase finalized` 退出码 0，stdout `PASS`**。
- **重复 `evidence-finalize` 退出码 0，`{"status": "finalized"}`**（幂等成立）。

结论：契约验收测试1 的端到端行为成立，且由我自建夹具独立复现。

### 2. 修复是承重的（回退 core.py）

把 `pipeline_tools/core.py` 临时替换为 `git show fe72596:pipeline_tools/core.py`，替换后目标文件 sha256 与 fe72596 版本一致（`1f9adb9870b49da2a1b614474f5c7b076016c51104f9f93dc9cb78967864a598`）。随后对该回退版本重跑同一自建夹具（`REV_ONLY_CHAIN=1`）：

- `snapshot_after_publish = ["finalization head is stale"]`
- `evidence verify --phase finalized` 退出码 **3**，stdout `FAIL: finalization head is stale`
- 重复 `evidence-finalize` 退出码 **3**，`{"status": "blocked", "missing": ["finalization head is stale"]}`

用后按字节还原：`moved_to_backup` → `cp` 回写，还原后 sha256 `8fbcde9f8bc057ba811d48405cb73498344fb6bbd556bece5228797f66fe8d02` == `HEAD` 中 core.py 的 sha256，`git status --porcelain` 空。

结论：修复是承重的——同一条链路在修复前失败、修复后通过。

### 3. 产品路径改动后仍 stale

自建夹具中，发布标记（HEAD 前移）后提交一个改动 `src/app.py` 的产品提交：

- `verify_finalization_snapshot` 返回**恰好** `["finalization head is stale"]`
- `evidence verify --phase finalized` 退出码 3，`FAIL: finalization head is stale`

结论：容忍未越界到产品改动，fail-closed 保持。

### 4. 非祖先 head 仍 stale

把标记 `identity.head` 改为非祖先的 `1`*40（40 位十六进制），在 HEAD 位于已发布标记提交时校验：

- 返回**恰好** `["finalization head is stale"]`

结论：非祖先/不可解析 head 仍被拒。

### 5. 快照失配仍拒绝

在 HEAD 位于已发布标记提交（head 判据满足，只剩快照判据）时篡改保留证据 `final-check.md`：

- `verify_finalization_snapshot` 返回**恰好** `["finalization retained evidence hash mismatch"]`（无 head 错误混入，说明容忍未掩盖 retention 判据）
- `planning evidence-finalize` 退出码 3，`{"status": "blocked", "missing": ["finalization retained evidence hash mismatch"], "finalization": null}`

结论：retention 快照判据未被本次改动波及。

### 6. `branch`/`worktree` 未被顺手放宽

在 HEAD 位于已发布标记提交时（head 判据满足）分别改写标记：

- `identity.branch = "some-other-branch"` → 返回**恰好** `["finalization branch is stale"]`
- `identity.worktree = "C:/definitely/elsewhere"` → 返回**恰好** `["finalization worktree is stale"]`

对照 `pipeline_tools/core.py` 现行代码：`branch`/`worktree` 分支中没有任何 `key == ...` 的容忍条件，只有 `head` 分支调用 `head_advanced_by_evidence_only`。`git diff fe72596 39c8984 -- pipeline_tools/core.py` 显示 `worktree` 的 `Path(...).resolve()` 规范化与相等比较逐字保留。

结论：`branch`/`worktree` 仍严格相等，未扩围（决策点 1 未触发）。

### 7. 既有断言完整性

- `git diff --numstat fe72596 39c8984 -- tests/` → `136  0  tests/test_planning.py`，即**删除行数为 0**，新增 136 行全为新增用例与助手。
- 逐行核对 `git diff fe72596 39c8984 -- tests/` 的删除侧：不存在任何 `-` 行（除 `---` 文件头），故本任务之前就存在的断言无一被删除或放宽。
- 全量测试由基线 392 增至 395（+3 新增用例），未减少。

结论：既有断言完整性成立。

### 8. 无越界

- `git diff --name-only fe72596 39c8984` → `pipeline_tools/core.py`、`references/merge-and-recovery.md`、`tests/test_planning.py`，全部落在 revision 1 的 `allowed_paths` 内。
- 全分支范围 `git diff --name-only fe72596 HEAD` → 上述 3 个文件 + `.pipeline/finalization-marker-head-tolerance/executor-report.md`、`executor-result.json`（均为本任务 `allowed_paths` 内的证据）。
- `git diff --name-only fe72596 HEAD -- <所有 forbidden_paths 目标>` 输出为空：`docs/goal.md`、三个依赖任务证据目录、两个 security-scan 证据目录**零改动**。
- `python -m pipeline_tools scope check . --task-id finalization-marker-head-tolerance --allowed … --forbidden …` 退出码 0，stdout `PASS`。
- `git diff --check fe72596 39c8984` 退出码 0（无空白/冲突标记问题）。

结论：无越界，forbidden_paths 零改动。

## 四条验收测试（逐条命令、cwd、退出码）

cwd 均为 `D:\Projects\Skills\pipeline\.worktrees\finalization-marker-head-tolerance`，均设 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

| 验收 | 命令 | 退出码 | 观察 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits` | 0 | `1 passed, 50 deselected` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k finalization_marker_head_is_still_stale_after_product_commits` | 0 | `1 passed, 50 deselected` |
| acceptance-test-3 | `python -m pytest -q tests/test_planning.py -k finalization_marker_snapshot_mismatch_is_still_rejected` | 0 | `1 passed, 50 deselected` |
| acceptance-test-4 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | `1 passed, 27 deselected` |

验收测试4 逐句核对：`references/merge-and-recovery.md` 的「合并后」小节（第 44 行起）新增段落明确写有——标记 `head` 等于当前 `HEAD`，**或**它是 `HEAD` 的祖先且两者之间只有该任务的证据提交（复用 `head_advanced_by_evidence_only`，证据目录取该任务证据目录）；标记 head 之后出现改动产品路径（或任何非证据路径）的提交仍报 `finalization head is stale`；`branch` 与 `worktree` 不适用该容忍；`retained_sha256` 失配仍报 `finalization retained evidence hash mismatch`；重复 `evidence-finalize` 仍返回 `finalized`。与实现行为逐条一致。

## 全量测试

- 命令：`python -m pytest -q`
- cwd：`D:\Projects\Skills\pipeline\.worktrees\finalization-marker-head-tolerance`
- 退出码：0
- 结果：`395 passed, 28 subtests passed in 278.39s (0:04:38)`

**与执行者声明的 `395 passed, 28 subtests passed` 完全一致，无差异。**

## 其它 CLI 检查

| 命令 | cwd | 退出码 |
|---|---|---|
| `python -m pipeline_tools task validate docs/tasks/finalization-marker-head-tolerance.md` | worktree | 0（`PASS`） |
| `python -m pipeline_tools result verify .pipeline/finalization-marker-head-tolerance/executor-result.json --task-id finalization-marker-head-tolerance --role executor` | worktree | 0（`PASS`） |
| `python -m pipeline_tools scope check . --task-id … --allowed … --forbidden …` | worktree | 0（`PASS`） |
| `git diff --check fe72596 39c8984` | worktree | 0 |

## 范围与既有断言完整性核对结果（汇总）

- `allowed_paths`：实现提交与分支尖端触及的全部路径均在许可清单内。
- `forbidden_paths`：零改动（含 `docs/goal.md`、三个依赖任务证据目录、两个 security-scan 证据目录）。
- `tests/` 删除行数 0，既有断言零削弱。
- `references/merge-and-recovery.md` 仅新增一段（3 增 1 改：把原有一行末尾拆为两段），原有事实句保留。

## 附带缺陷（属于本任务证据集，非被审提交 39c8984 的代码；由主代理/执行者处置）

`evidence verify` 对所有报告的 `evidence_refs` 逐项调用 `_evidence_file_exists`（`pipeline_tools/core.py:674`），该函数把不以 `.pipeline/` 开头的引用解析为**证据目录内**的相对路径（`pipeline_tools/core.py:455-467`）。因此仓库根相对的产品文件路径不可解析。

- 执行者的 `executor-report.md` 的 `evidence_refs` 含 4 条根相对产品路径（`pipeline_tools/core.py`、`tests/test_planning.py`、`references/merge-and-recovery.md`、`docs/tasks/finalization-marker-head-tolerance.md`），`evidence verify --phase active` 与 `--phase finalized` 都会因此报 4 条 `executor-report.md evidence_ref is missing or not relative`。
- 最小复现：在 worktree 内 `python -m pipeline_tools evidence verify .pipeline/finalization-marker-head-tolerance --task-id finalization-marker-head-tolerance --phase finalized` → 退出码 3，输出含 4 条上述错误（另含尚无 `final-check.md`/`finalization.json` 的缺件，属合并前正常）。
- 影响面：这是**既有普遍模式**而非本次回归——我扫描全仓库证据，23 个报告文件存在同类不可解析引用（如 `.pipeline/pipeline-tools-v1/*`、`.pipeline/task-evidence-reconcile/*`），历史任务在同样形态下仍被最终化。
- 为何不改变本报告结论：最终化的实际操作路径 `planning._finalize_evidence_unlocked`（`pipeline_tools/planning.py:2583`）只要求 `evidence_refs` 是**非空列表**，不解析引用（`_validate_finalization_report`，`pipeline_tools/planning.py:2413`），故 post-merge gate → `evidence-finalize` → 标记 → 重复 `evidence-finalize` 全部不受影响；契约的四条验收与全量测试也全部通过。
- 建议：主代理（有权改证据）把 `executor-report.md` 的 4 条产品路径引用改为证据目录内引用（如 `.pipeline/finalization-marker-head-tolerance/executor-report.md`），或为其生成证据目录内的输出日志文件，以免 `evidence verify --phase finalized` 在本任务最终化后仍报错。本审查不得修改该文件。

## 未验证（unverified）

- 契约 `unknown-2`：既有 16 个历史 `finalization.json` 在修正规则下有多少能通过，未枚举（也未读取或改动任何历史证据目录）。
- 未在真实主仓库上执行 `gate post-merge`；所有端到端均使用自建临时仓库。
- 未覆盖「分支非 `main` 时在主工作树最终化」等非常规现场。

## 阻塞（blockers）

- 无（对 `39c8984` 的实现审查本身无阻塞；上述证据引用缺陷不阻碍 `finalize_evidence` 路径，仅影响 `evidence verify --phase finalized` 的通过，交由主代理处置）。

## findings（契约本身）

- 无。契约的判据与实现行为一致，未发现需要单列为契约缺陷的问题。

## 结论

**PASS**。修复针对性地解除了标记 head 的循环不可满足，且自建夹具证明修复承重（回退即失败）；产品路径改动、非祖先 head、快照失配、`branch`/`worktree` 均仍 fail-closed；既有断言零削弱、范围零越界；全量测试 395 passed / 28 subtests 与声明一致。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "finalization-marker-head-tolerance",
  "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
  "branch": "finalization-marker-head-tolerance",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "head": "39c8984b98dee0cd5669d5e670547e777bee794b",
  "sheet_revision": 1,
  "sheet_sha256": "b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76",
  "observed_at_commit": "c67734009870e4886a606efc8a52d47e219fcd88",
  "generated_at": "2026-10-09T00:36:00+00:00",
  "commands": [
    {
      "command": "git rev-parse --show-toplevel",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "git merge-base --is-ancestor 39c8984b98dee0cd5669d5e670547e777bee794b HEAD",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pipeline_tools task validate docs/tasks/finalization-marker-head-tolerance.md",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_is_still_stale_after_product_commits",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_marker_snapshot_mismatch_is_still_rejected",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pytest -q",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pipeline_tools result verify .pipeline/finalization-marker-head-tolerance/executor-result.json --task-id finalization-marker-head-tolerance --role executor",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pipeline_tools scope check . --task-id finalization-marker-head-tolerance --allowed pipeline_tools/core.py tests/test_planning.py references/merge-and-recovery.md docs/tasks/finalization-marker-head-tolerance.md .pipeline/finalization-marker-head-tolerance/** --forbidden docs/goal.md .pipeline/finalization-and-reconcile-phase/** .pipeline/post-merge-evidence-identity/** .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/** .env credentials/**",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "git diff --check fe72596fb2ba134549f9f269b8844a83bc9d5da0 39c8984b98dee0cd5669d5e670547e777bee794b",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "git diff --numstat fe72596fb2ba134549f9f269b8844a83bc9d5da0 39c8984b98dee0cd5669d5e670547e777bee794b -- tests/",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\finalization-marker-head-tolerance",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "REV_ONLY_CHAIN=1 REV_TOOLS=<worktree> python rev_finalization_check.py  (self-built temp-repo fixture: merge -> gate post-merge -> evidence-finalize -> commit marker -> verify -> repeat finalize)",
      "cwd": "C:\\Users\\alexc\\AppData\\Local\\Temp",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "REV_ONLY_CHAIN=1 REV_TOOLS=<worktree> python rev_finalization_check.py  (same fixture, pipeline_tools/core.py temporarily reverted to fe72596; the inner CLI evidence verify returned FAIL)",
      "cwd": "C:\\Users\\alexc\\AppData\\Local\\Temp",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pipeline_tools evidence verify <tmp-repo>/.pipeline/rev-demo --task-id rev-demo --phase finalized  (run inside the self-built fixture with pipeline_tools/core.py reverted to fe72596 -- deliberate fail-closed observation)",
      "cwd": "C:\\Users\\alexc\\AppData\\Local\\Temp",
      "exit_code": 3,
      "expected_exit_code": 3,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    },
    {
      "command": "python -m pipeline_tools evidence verify <tmp-repo>/.pipeline/rev-demo --task-id rev-demo --phase finalized  (run inside the self-built fixture with the shipped fix in place -- deliberate pass observation)",
      "cwd": "C:\\Users\\alexc\\AppData\\Local\\Temp",
      "exit_code": 0,
      "evidence_ref": ".pipeline/finalization-marker-head-tolerance/review-report.md"
    }
  ],
  "assertions": [
    "The self-built temp-repo chain (merge -> gate post-merge -> evidence-finalize -> commit finalization.json -> verify) passes: verify_finalization_snapshot returns [] and evidence verify --phase finalized exits 0",
    "Committing the marker moves HEAD (published != merged) with a commit range containing exactly .pipeline/rev-demo/finalization.json",
    "A repeated planning evidence-finalize after the marker commit still returns {\"status\": \"finalized\"} (idempotent)",
    "With pipeline_tools/core.py byte-restored to fe72596, the same chain fails: snapshot=['finalization head is stale'], evidence verify exit 3, repeat finalize blocked -- so the fix is load-bearing",
    "A product-path commit after the marker head still returns exactly ['finalization head is stale'] (CLI evidence verify exit 3)",
    "A marker head set to a non-ancestor 40-hex value still returns exactly ['finalization head is stale']",
    "branch is still strict: changing identity.branch returns exactly ['finalization branch is stale']; worktree likewise returns exactly ['finalization worktree is stale']",
    "A tampered retained evidence file returns exactly ['finalization retained evidence hash mismatch'] and planning evidence-finalize returns blocked",
    "git diff --numstat fe72596 39c8984 -- tests/ is '136 0' -- zero deleted lines, so no pre-existing assertion was removed or weakened",
    "git diff --name-only fe72596 HEAD touches only allowed_paths; no forbidden path (docs/goal.md, three dependency evidence dirs, two security-scan evidence dirs) changed",
    "Full suite: 395 passed, 28 subtests passed -- identical to the executor's claim",
    "All four contract acceptance test commands exit 0",
    "core.py was restored byte-for-byte after the revert experiment (sha256 matches HEAD version; git status clean)"
  ],
  "evidence_refs": [
    ".pipeline/finalization-marker-head-tolerance/review-report.md",
    ".pipeline/finalization-marker-head-tolerance/reviewer-result.json"
  ],
  "unverified": [
    "Contract unknown-2: how many of the sixteen existing finalization.json markers would pass under the corrected rule was not enumerated; no historical evidence directory was read or modified.",
    "No gate post-merge was run against the real repository; all end-to-end runs used reviewer-built temporary repositories.",
    "Unconventional sites such as finalizing inside the task worktree were not exercised."
  ],
  "findings": [
    "pipeline_tools/core.py:674 resolves every evidence_refs entry relative to the evidence directory unless it starts with '.pipeline/' (core.py:455-467), so the executor-report.md published in this task's evidence set carries four root-relative product paths (pipeline_tools/core.py, tests/test_planning.py, references/merge-and-recovery.md, docs/tasks/finalization-marker-head-tolerance.md) that evidence verify reports as 'executor-report.md evidence_ref is missing or not relative' in both --phase active and --phase finalized. Repro: python -m pipeline_tools evidence verify .pipeline/finalization-marker-head-tolerance --task-id finalization-marker-head-tolerance --phase finalized -> exit 3. This is a pre-existing widespread evidence pattern (23 report files across the repo), not a regression from 39c8984, and it does not affect the finalization path because planning._finalize_evidence_unlocked (planning.py:2583) only requires evidence_refs to be a non-empty list (_validate_finalization_report, planning.py:2413). The main agent should repoint those four refs into the evidence directory before finalization.",
    "No defect found in the contract itself: the stated criteria match the implemented behavior."
  ],
  "blockers": [],
  "recommendation": "ready_for_merge"
}
```
