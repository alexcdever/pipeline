# test-metrics-isolation — 主代理最终检查

- task-id：`test-metrics-isolation`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/test-metrics-isolation`
- branch：`test-metrics-isolation`
- role：main-final（第三层验证）
- 冻结基线 HEAD：`14a17d2c62aa4765b53bc099af4dbb8c0e10998f`
- 结论：**PASS**

## 1. 身份与现场核对

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| task_id | `test-metrics-isolation` | 任务单与证据身份字段 | 一致 |
| branch | `test-metrics-isolation` | `git branch --show-current` | 一致 |
| worktree | `.worktrees/test-metrics-isolation` | `git worktree list` | 一致 |
| 冻结基线 | `14a17d2…`（含已合并的上一任务） | `git rev-parse HEAD` | 一致 |
| goal sha256 | `9abb196a…086e25f` | `sha256sum goal.md` | 一致 |
| 冻结任务单未被改动 | 期望无 diff | `git diff --name-only 14a17d2 -- docs/` 为空 | 一致 |

**调度前 reconcile（记录在案）**：任务 ② 的 worktree 原建自 `b5f7648`（上一任务合并前），与任务 ① 修改同一批文件。执行前已把该分支 `--ff-only` 快进到当时 `main`（`14a17d2`），分支零提交、无内容丢失；任务单未动且校验仍 pass。若不做此步，后续合并必然在同文件冲突。

## 2. 三份报告与机器结果

`.pipeline/test-metrics-isolation/` 含 `executor-report.md`、`review-report.md`、`final-check.md`、
`executor-result.json`、`reviewer-result.json`、`final-result.json`。无 `.log`、无 `.jsonl`。
markdown 侧 `status` 为大写 `PASS`；JSON 侧 `status` 为小写 `pass`。

## 3. 独立重跑关键验收（主代理亲自执行）

| 验收 ID | 退出码 |
|---|---|
| acceptance-test-cli-suite-leaves-tracked-metrics-unchanged | 0 |
| acceptance-test-auto-metrics-enabled-run-isolated | 0 |
| acceptance-test-wrapper-exit-code-with-isolation | 0 |
| acceptance-test-metrics-contract-documents-test-isolation | 0 |

## 4. 原始缺陷的端到端证明（本任务的核心）

主代理在 worktree 内，两次快照之间只跑一次全量测试，中间不插入任何 `pipeline-tools` 调用：

```
BEFORE_UNTRACKED=15  BEFORE_TOTAL=1450
python -m unittest discover -s tests  →  Ran 312 tests … OK, exit 0
AFTER_UNTRACKED=15   AFTER_TOTAL=1450
```

`.pipeline/metrics/` 未增长。基线 309 + 新增 3 = 312。原始缺陷（每跑一次套件固定 +1 未跟踪文件）已消除。

## 5. 抽查高风险断言

- 亲自阅读 `git diff 14a17d2 -- tests/ references/`：3 文件，+113/−5。
- 隔离仅在「自动指标将被启用」时触发；临时 root 为非仓库目录并 `atexit` 清理。
- `run_cli` 现注入 `PYTHONPATH`，使异 cwd 下仍能导入本 checkout——这是测试 2 成立的必要条件。
- 断言非套话：套件不变测试比较仓库 metrics 目录的前后快照；wrapper 测试断言外层命令真实退出码 7 在隔离生效时仍传播。
- 既有自动指标测试未被跳过或删除（55 → 57 个测试方法，新增 2，无删除，无新增 skip）。

## 6. 范围与非目标

`git diff --name-only 14a17d2` 仅 `tests/`、`references/`。`pipeline_tools/`、`.gitignore`、`docs/tasks/`、已入库的 `.pipeline/metrics/` 历史均未改动。

## 7. 未验证项与已登记跟进

- **审查发现的非阻塞弱点**：文档契约测试末尾的负向断言使用了 `加入`，而文档措辞为 `加进`，该条 `assertNotIn` 恒真、实际不设防。正向内容断言真实有效，不影响本任务判定。属可后续修的小瑕疵，为避免在独立审查后改动被测代码而使审查证据失效，本任务不就地修改，登记为跟进项。
- 未核验隔离临时 root 内单条事件的内容（仅核验数量/集合增长）。
- 未在非 Windows 平台复跑。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "test-metrics-isolation",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/test-metrics-isolation",
  "branch": "test-metrics-isolation",
  "role": "main-final",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_cli_suite_leaves_tracked_metrics_unchanged",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/test-metrics-isolation",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/test-metrics-isolation",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/test-metrics-isolation",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/test-metrics-isolation",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/test-metrics-isolation",
      "evidence_ref": "final-check.md"
    }
  ],
  "assertions": [
    "4 条验收测试由主代理亲自重跑，退出码全为 0",
    "全量 312 tests OK；套件跑完后 .pipeline/metrics/ 未增长（15/1450 → 15/1450），原始缺陷已消除",
    "改动仅 3 个文件，全在 allowed_paths 内；pipeline_tools/、.gitignore、docs/、已入库 metrics 历史均未动",
    "既有自动指标测试未被跳过或删除",
    "证据目录无 .log/.jsonl，三份报告与三份 JSON 齐全且身份一致",
    "调度前已记录并执行 worktree 分支的 --ff-only reconcile"
  ],
  "evidence_refs": ["final-check.md", "executor-report.md", "review-report.md"],
  "unverified": [
    "文档契约测试的负向断言（加入 vs 加进）恒真，不设防，登记为跟进项",
    "未核验隔离临时 root 内单条事件内容",
    "未在非 Windows 平台复跑"
  ],
  "recommendation": "ready_to_merge"
}
```