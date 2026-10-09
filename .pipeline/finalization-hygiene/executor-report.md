# executor-report：finalization-hygiene

## 任务身份

- task-id：`finalization-hygiene`
- task-type：`repair`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene`
- branch：`finalization-hygiene`
- baseline HEAD：`e75c787c73f51fc9c68dba79dc9a82d8d4bb6af1`
- 实现提交：`f21189248027ed7b37ce7e7e2c847fb659aa7c19`
- role：executor，round 1
- sheet_revision：1
- sheet_sha256：`c1a06b454c6f904755989a0cbb8881ebdf9d53677e3bbddb62a206000fb98b2e`

## 环境检查（逐项）

| # | 检查 | 命令 | 结果 |
|---|---|---|---|
| 1 | worktree 根 | `git -C <worktree> rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene` ✓ |
| 2 | branch | `git -C <worktree> branch --show-current` | `finalization-hygiene` ✓ |
| 3 | 契约可用 | `python -m pipeline_tools task validate docs/tasks/finalization-hygiene.md` | 退出码 0（PASS）✓ |
| 4 | pytest 可用 | `python -m pytest --version` | `pytest 9.1.1` ✓ |
| 5 | 证据目录可写 | 创建并删除探针文件 | 可写 ✓ |
| 6 | 不新建 worktree、不动主工作树 | 全部命令 cwd = 本 worktree；未执行 `git worktree add`；未写入主工作树与其它任务证据目录 | ✓ |

## 缺陷与修复

### A 最终化剪枝不再删除本地状态文件

`_finalize_evidence_unlocked`（`pipeline_tools/planning.py`）原本只保留 `RETAINED_EVIDENCE_NAMES`（三份报告 + 三份机器结果 + `finalization.json`）并剪掉其余文件，`goal.json` 与 `amendments.json` 也在被剪之列。`amendments.json` 是修订链的唯一载体，删掉后 `task_sheet_revision` 退化为 1，与报告声明的 `sheet_revision` 不符，`evidence verify --phase finalized` 直接失败。

修复：

- `pipeline_tools/core.py:36-42` 新增模块常量 `LOCAL_STATE_FILE_NAMES = ("goal.json", "amendments.json")`，并保留原注释说明：这两个文件是本地状态而非证据，与保留集并列但**不进入** `retained_sha256` 快照，因此 retention 快照判据逐字未变。
- `pipeline_tools/planning.py:2595-2601`：`retained` 仍是 `RETAINED_EVIDENCE_NAMES`；新增 `local_state`（存在才列入）与 `spared = set(retained) | set(local_state)`。
- `pipeline_tools/planning.py:2693-2699`：剪枝跳过集合由 `set(retained)` 改为 `spared`，因此 `goal.json`/`amendments.json` 留下，其余非保留文件（原始日志、临时产物）仍照现行为剪掉。
- `pipeline_tools/planning.py:2668`：悬空引用检查的允许集合改为 `spared`。该检查的语义是"被引用的文件是否会被删掉"，两个本地状态文件既已不再被删，就不应再把对它们的引用判为"would be deleted or is unsafe"。标记文件的 `retained` 字段与 `retained_sha256` 快照一字未改。

### B "仅证据提交"的范围放宽到整个 `.pipeline/`

`head_advanced_by_evidence_only` 原本把"仅证据提交"限定为**该任务自己的**证据目录（外加 `.pipeline/metrics/`），因此别的任务提交自己的证据会被判为产品提交，已关闭任务重跑 `--phase finalized` 报 `finalization head is stale`。

修复（`pipeline_tools/core.py`）：

- `evidence_only_paths` 改为只接收 `changed_paths`，判据是**路径本身**：规范化后落在 `.pipeline/` 子树（该任务或任意别的任务的证据目录、`.pipeline/metrics/`、`.pipeline/planning/`）即算证据路径；`.pipeline` 之外的任何改动都不算。函数签名中的 `root`/`evidence_directory` 已无判据作用，故一并移除，避免留下决定性已消失的"死参数"。
- `head_advanced_by_evidence_only` 同步去掉 `evidence_directory` 形参，两处调用点（`core.py:599` 的 schema-2 报告 head 检查、`core.py:1196` 的 `verify_finalization_snapshot`）与 `evidence_freshness` 的调用点（`core.py:1830`）同步更新。

### fail-closed（契约 unknowns 明确要求）

`evidence_only_paths` 是"每个改动路径都必须是证据路径"的全称判断，因此：

- **混合提交**（同一提交同时改动证据路径与产品路径）→ 产品路径那一条不满足 → 返回 `False` → 判为非仅证据提交。实测见下"混合提交 fail-closed"。
- **路径无法解析**（空串、绝对路径、`X:/` 盘符路径、含 `..` 的遍历路径）→ 立即返回 `False`，判为非仅证据提交。
- 提交区间本身无法解析（`reported_head` 不是合法提交、不是 `HEAD` 祖先，或 `git diff` 失败使 `changed_paths_between` 返回 `None`）→ `head_advanced_by_evidence_only` 返回 `False`，仍报 `finalization head is stale`。

两条都由 `EvidenceTests.test_finalized_verification_still_fails_after_product_commits` 覆盖。

### 未波及（逐项确认）

- retention 快照判据：`retained_evidence_snapshot` 与 `RETAINED_EVIDENCE_NAMES` 未改；`tests/test_git_checks.py:294`（保留集逐字等于 7 个名字）与 `tests/test_acceptance_id_and_template_compliance.py:237`（保留集与文档一致）继续通过。
- 产品路径失效判据：产品路径仍非证据路径，`finalization head is stale` 与 `<report> head does not match current Git identity` 的错误文本与触发条件未改。
- schema 与报告结构校验：`finalization.json` 的字段集合、`_validate_finalization_report`、`_validate_result`、`_read_evidence_block`、`_read_machine_evidence` 全部未改。
- 既有断言：本任务之前就存在的断言一个都没有删除或放宽（全量用例从 398 增至 401，只增不减；`28 subtests` 不变）。

## 文档

- `references/merge-and-recovery.md`：
  - "最终化标记的 head 判据"段改为记录放宽后的证据路径判据（任意任务的证据目录、`.pipeline/metrics/`、`.pipeline/planning/` 都算，`.pipeline` 之外不算），并写明混合提交与区间无法解析时 fail-closed。
  - 新增"**复验窗口**"段：关闭时的那次 `finalized verify`/`gate post-merge` 通过即算通过，标记不必被重刷；之后只有产品路径提交会让记录的 `head` 合法变旧（此时重新复验，不改写/删除标记），证据路径提交不会。
  - 新增"**保留的本地状态文件**"段：保留集之外额外保留 `goal.json`（schema 1-3 为 `implement-plan.json`）与 `amendments.json`，二者是本地状态、不进入 `retained_sha256`、不随证据提交进入 Git，其余非保留过程产物仍照旧剪掉，并说明删掉修订链会让工具读到的修订退化。
  - "证据身份的阶段分工"段中"仅被本任务证据提交推进"同步改为放宽后的判据，避免同一文件内自相矛盾。
- `SKILL.md`：`active` 阶段 head 判据改为 `.pipeline/**` 全域；第 7 条"合并后复验"补一句复验窗口语义（关闭时通过即算通过；之后仅产品提交会让 head 合法变旧；混合提交 fail-closed）；第 8 条"持久化"注明成功最终化后额外保留两个本地状态文件。版本号未改（见 `unverified`）。

## 混合提交 fail-closed 的实现与实测

- 实现：`evidence_only_paths` 对每个改动路径做全称判断（任一路径不满足即 `False`），混合提交天然不满足，不需要额外的"混合"分支。
- 实测（新用例 `test_finalized_verification_still_fails_after_product_commits` 的 (b) 分支）：任务关闭并提交标记后，提交同时改动 `.pipeline/demo/scratch.md` 与 `src/app.py` 的混合提交，`git diff --name-only` 确认两条路径都在区间内，`verify_finalization_snapshot` 返回 `["finalization head is stale"]`。
- 反向实测（临时实验，已还原）：把 `evidence_only_paths` 中"非 `.pipeline` 路径一律返回 False"的判据去掉（即把一切都当证据），该用例立刻失败——`(a)` 产品提交分支得到 `[]` 而不是 `finalization head is stale`，证明这条 fail-closed 判据是被真实观测到的、不可移除的。

## 端到端演示

脚本位于系统临时目录（`C:/Users/alexc/AppData/Local/Temp/fh-e2e-demo.py`），在临时仓库里跑完整链路，输出日志见 `e2e-demo.log`（同目录，本地过程产物，见 `unverified`）。链路与退出码：

1. 临时仓库：任务分支写三份 schema-2 报告 + 三份机器结果 + `final-result.json` 的 `decision`，提交后 `git merge --no-ff`。
2. 主工作树证据目录写入本地状态文件：`amendments.json`（revision 2，`sheet_sha256` = `b`×64）、`goal.json`（`task_sheet_sha256` = 同一值），报告声明 `sheet_revision: 2`；再放一个 `raw-process.log`。
3. `python -m pipeline_tools gate post-merge .pipeline/demo --task-id demo --branch main` → 退出码 0（PASS）。
4. `python -m pipeline_tools planning evidence-finalize .pipeline/demo --task-id demo --success` → 退出码 0，`{"status": "finalized", "missing": [], ...}`。
5. 最终化后目录内容：`.lifecycle.lock`、`amendments.json`、`executor-report.md`、`executor-result.json`、`final-check.md`、`final-result.json`、`finalization.json`、`goal.json`、`review-report.md`、`reviewer-result.json` —— 保留集 7 件 + 两个本地状态文件 + 既有 `.lifecycle.lock`；`raw-process.log` 已被剪掉。
6. `task_sheet_revision(root, 'demo')` 读回 2（预期 2）——修订链仍在。
7. 提交标记：`git add .pipeline/demo/finalization.json && git commit` → `python -m pipeline_tools evidence verify .pipeline/demo --task-id demo --phase finalized` → 退出码 0（PASS）。
8. 提交另一个任务的证据：`.pipeline/other-task/executor-report.md` 提交，`HEAD` 从 `64f9140e...` 移到 `104005336...`；再次 `evidence verify --phase finalized` → **退出码 0（PASS）**。
9. 负向对照（额外观测）：再提交一个产品路径改动（`src/app.py`）→ `evidence verify --phase finalized` → 退出码 3，`FAIL: finalization head is stale`（产品路径仍然 fail-closed）。
10. 脚本汇总输出 `RESULT: PASS`，脚本退出码 0。

## 既有失效行为的回归验证（临时实验，已全部还原）

- 把 `planning.py` 的剪枝跳过集合改回 `set(retained)`：`test_finalization_keeps_local_state_files` 失败于 `goal.json` 被删（`AssertionError: False is not true`）。
- 把 `evidence_only_paths` 收窄回"只有本任务证据目录"：`test_finalized_verification_survives_another_tasks_evidence_commit` 失败于 `['finalization head is stale'] != []`。
- 实验后均从备份还原；`git diff` 只剩本任务预期的改动。

## 改动文件

- `pipeline_tools/core.py`：新增 `LOCAL_STATE_FILE_NAMES`；`evidence_only_paths` 重写为 `.pipeline/**` 全域判据并 fail-closed；`head_advanced_by_evidence_only` 去掉不再起判据作用的 `evidence_directory` 形参；三处调用点同步。
- `pipeline_tools/planning.py`：导入 `LOCAL_STATE_FILE_NAMES`；`_finalize_evidence_unlocked` 的剪枝与悬空引用检查改用 `spared`。
- `tests/test_planning.py`：新增 `_revision_chain_evidence_dir` 辅助与 `PlanningTests` 下两条验收用例。
- `tests/test_evidence.py`：新增 `EvidenceTests` 下一条验收用例（含产品提交与混合提交两个分支）。
- `references/merge-and-recovery.md`、`SKILL.md`：文档同步。

未改动：`docs/goal.md`；任何历史任务单与历史证据；五个已完成任务的证据目录（`task-sheet-revision-and-evidence-binding`、`post-merge-evidence-identity`、`finalization-and-reconcile-phase`、`finalization-marker-head-tolerance`、`finalization-report-reader`）。未改写任何报告文件。

## 验收测试

| ID | 测试 | 命令 | 退出码 |
|---|---|---|---|
| acceptance-test-1 | `PlanningTests.test_finalization_keeps_local_state_files` | `python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files` | 0 |
| acceptance-test-2 | `PlanningTests.test_finalized_verification_survives_another_tasks_evidence_commit` | `python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit` | 0 |
| acceptance-test-3 | `EvidenceTests.test_finalized_verification_still_fails_after_product_commits` | `python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits` | 0 |
| acceptance-test-4 | `AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`（既有用例，未改动） | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 |

- 验收测试1：`_merged_finalization_repo` 造出已合并任务，放入 revision 2 的 `amendments.json`、`goal.json` 与一个无关过程文件 `raw-process.log`；走 `gate post-merge` → `planning evidence-finalize` 完整链路。断言 `goal.json`/`amendments.json` 仍在且 `goal.json` 字节未变、`task_sheet_revision` 读回 2、`_recorded_task_sheet_sha256` 读回链上的哈希、保留集 7 件齐全、`raw-process.log` 被剪、目录内除保留集与两文件与 `.lifecycle.lock` 外无残留。
- 验收测试2：任务关闭并提交标记后，提交一份只动 `.pipeline/other-task/executor-report.md` 的证据提交；断言 `verify_finalization_snapshot` 为 `[]`、标记文件仍在且字节未变、标记身份 head 仍是合并提交、`evidence verify --phase finalized` 退出码 0。达标方式是放宽判据，不是删除标记或改写身份。
- 验收测试3：同一用例内两个分支——(a) 只动产品路径的提交使 `verify_finalization_snapshot` 报 `finalization head is stale`；(b) 同时动 `.pipeline/demo/scratch.md` 与 `src/app.py` 的混合提交同样报 `finalization head is stale`。
- 验收测试4：既有文档一致性用例原样通过。

全量测试：`python -m pytest -q`（cwd = worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）→ 退出码 0，`401 passed, 28 subtests passed`（基线 398 passed + 本任务新增 3 条验收用例）。

## 其它检查

- `python -m pipeline_tools task validate docs/tasks/finalization-hygiene.md` → 退出码 0（PASS）。
- `python -m pipeline_tools result verify .pipeline/finalization-hygiene/executor-result.json --task-id finalization-hygiene --role executor` → 退出码 0。
- `python -m pipeline_tools scope check . --task-id finalization-hygiene --allowed pipeline_tools/core.py pipeline_tools/planning.py tests/test_planning.py tests/test_evidence.py references/merge-and-recovery.md SKILL.md docs/tasks/finalization-hygiene.md .pipeline/finalization-hygiene/** --forbidden docs/goal.md .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/finalization-report-reader/** .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/** .env credentials/**` → 退出码 0（PASS）。
- `git diff --check` → 退出码 0。

## 决策点核查

1. 混合提交无法机械判定性质 —— 未触发：混合提交由"每个改动路径都必须是证据路径"的全称判断机械判定，且 fail-closed，有测试钉住。
2. 既有断言必须被实质性削弱才能通过 —— 未触发：既有断言一字未改，全量 401 passed。
3. 保留本地状态文件会破坏 retention 快照判据或既有最终化校验 —— 未触发：`retained_sha256` 的取值集合（`RETAINED_EVIDENCE_NAMES` 去掉 `finalization.json`）未变，快照失配仍报 `finalization retained evidence hash mismatch`（`test_finalization_marker_snapshot_mismatch_is_still_rejected` 继续通过）；标记字段结构未改。
4. 实现必须修改契约未列出的文件 —— 未触发：`git status --porcelain` 只显示 `allowed_paths` 内的改动。

```pipeline-evidence
{"schema": 2, "task_id": "finalization-hygiene", "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "branch": "finalization-hygiene", "role": "executor", "round": 1, "status": "PASS", "head": "f21189248027ed7b37ce7e7e2c847fb659aa7c19", "sheet_revision": 1, "sheet_sha256": "c1a06b454c6f904755989a0cbb8881ebdf9d53677e3bbddb62a206000fb98b2e", "observed_at_commit": "f21189248027ed7b37ce7e7e2c847fb659aa7c19", "generated_at": "2026-10-09T10:55:00+00:00", "commands": [{"command": "git -C D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene rev-parse --show-toplevel", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git -C D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/finalization-hygiene.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest --version", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python C:/Users/alexc/AppData/Local/Temp/fh-e2e-demo.py D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools result verify .pipeline/finalization-hygiene/executor-result.json --task-id finalization-hygiene --role executor", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --task-id finalization-hygiene --allowed pipeline_tools/core.py pipeline_tools/planning.py tests/test_planning.py tests/test_evidence.py references/merge-and-recovery.md SKILL.md docs/tasks/finalization-hygiene.md .pipeline/finalization-hygiene/** --forbidden docs/goal.md .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/finalization-report-reader/** .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/** .env credentials/**", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools evidence verify .pipeline/demo --task-id demo --phase finalized  # last step of the e2e demo: after a product-path commit, deliberately failing", "cwd": "C:/Users/alexc/AppData/Local/Temp/fh-e2e-u_6mwpyy/repo", "exit_code": 3, "expected_exit_code": 3, "evidence_ref": "executor-report.md"}], "assertions": ["finalization keeps goal.json and amendments.json while still pruning an unrelated process artifact, and the retained evidence set of seven names is unchanged", "the revision chain read back after finalization is the revision the reports declared, so a later revision-bound finalized check no longer fails", "a task closed and marked as finalized still passes evidence verify --phase finalized after another task commits its own .pipeline evidence", "a product-only commit and a mixed evidence-plus-product commit both still make the finalized marker stale, so the widened scope stays fail-closed", "the widened evidence-only basis is path-based: any .pipeline/** path counts and every path outside .pipeline does not", "the retention hash snapshot stays byte-identical to RETAINED_EVIDENCE_NAMES, and the finalization marker structure is unchanged", "no pre-existing assertion was deleted or relaxed: the full suite grew from 398 to 401 passing tests with the 28 subtests unchanged"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["the end-to-end demo log e2e-demo.log is a local process artifact inside the evidence directory: it is intentionally not referenced by this report because finalization prunes it, and it is not committed to Git", "references/acceptance-evidence.md and references/execution-and-review.md still describe the evidence-only basis as 'this task's own evidence directory'; those files are outside this task's allowed_paths, so the widened scope is documented only in references/merge-and-recovery.md and SKILL.md", "SKILL.md keeps version 0.16.0: a version bump would normally be paired with a changelog entry in references/compat-and-migration.md, which is outside this task's allowed_paths", "whether any of the other finalized task directories still hold a local state file whose absence changes a current check was not enumerated; only this task's behaviour was measured"]}
```
