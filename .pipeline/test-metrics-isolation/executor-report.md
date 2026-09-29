# 执行报告：test-metrics-isolation

- **task-id**：test-metrics-isolation
- **worktree**：`D:\Projects\Skills\pipeline\.worktrees\test-metrics-isolation`
- **branch**：`test-metrics-isolation`
- **HEAD**：`14a17d2c62aa4765b53bc099af4dbb8c0e10998f`
- **角色**：executor
- **轮次**：1
- **状态**：PASS
- **测试数量**：312（基线 309 + 新增 3 个测试）

## 问题与根因

跑整套测试会污染受追踪的 `.pipeline/metrics/`：每次运行新增一个未追踪的 `*.json`，弄脏工作树。`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 挡不住，因为 `tests/test_cli.py` 在若干用例里显式把该开关设回 `'0'`，以真正覆盖自动采集路径。

根因（逐条核验）：

1. `run_cli` 的 `cwd` 默认是仓库根，而自动采集按 cwd 解析项目根（`pipeline_tools/__main__.py` 的 `_git_root(Path.cwd())`），于是 `metric_event` 写入真实 `.pipeline/metrics/`（`pipeline_tools/core.py` 的 `_metrics_dir`）。
2. `tests/test_cli.py` 的 `test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code` 用 `command run --cwd str(ROOT)` 且把开关设 `0`/`1`，是唯一在整套运行时仍污染仓库的用例（实测每轮 +1 个未追踪文件）。

## 修复（仅测试侧）

- `tests/test_cli.py`
  - 新增 `auto_metrics_requested(env)`：判断某环境映射是否让自动采集保持开启。
  - 新增 `isolated_metrics_root()`：`tempfile.mkdtemp` 临时 root，`atexit` 清理；启用自动采集时，`run_cli` 默认 cwd 指向它，使根解析落在非仓库临时树。
  - `run_cli` 现固定把 `ROOT` 注入 `PYTHONPATH`，保证换 cwd 后仍能导入本仓库的 `pipeline_tools`。
  - 新增 `metrics_snapshot(directory)`：名称→内容哈希，用于断言仓库 metrics 未被写入。
  - 改写 wrapper 用例：在临时 root 内运行，并断言（a）外层命令真实退出码 7 仍传播、（b）仓库 `.pipeline/metrics/` 快照不变、（c）临时 root 下确实产生了 metrics 事件。
  - 新增 `test_cli_suite_leaves_tracked_metrics_unchanged` 与 `test_auto_metrics_enabled_run_keeps_metrics_out_of_repository`。
- `tests/test_acceptance_id_and_template_compliance.py`
  - 新增 `test_references_metrics_contract_documents_test_isolation`，断言 `references/metrics-contract.md` 的测试隔离规则真实内容。
- `references/metrics-contract.md`
  - 新增「测试隔离规则」一节，记录根因、隔离要求与 `git status --short .pipeline/metrics/` 的验收口径。

未改动 `pipeline_tools/` 生产行为；`.pipeline/metrics/` 的追踪状态与 `.gitignore` 未动；`docs/tasks/` 下冻结任务单未改。

## 验收结果

| 验收 ID | 命令 | 退出码 | 结果 |
|---|---|---|---|
| acceptance-test-cli-suite-leaves-tracked-metrics-unchanged | `python -m unittest tests.test_cli.CLITests.test_cli_suite_leaves_tracked_metrics_unchanged` | 0 | OK |
| acceptance-test-auto-metrics-enabled-run-isolated | `python -m unittest tests.test_cli.CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository` | 0 | OK |
| acceptance-test-wrapper-exit-code-with-isolation | `python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code` | 0 | OK |
| acceptance-test-metrics-contract-documents-test-isolation | `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation` | 0 | OK |

## 原始 bug 已修复（端到端证据）

完整套件运行前后对仓库 `.pipeline/metrics/` 计数（worktree 内，期间无其它工具调用干扰）：

```
BEFORE_UNTRACKED=4 BEFORE_TOTAL=1439
SUITE_EXIT=0
AFTER_UNTRACKED=4 AFTER_TOTAL=1439
Ran 312 tests in 237.642s
OK
```

未追踪文件数与总文件数在整套运行前后均不变，验证原始污染已消除。

## 范围与契约核验

- `python -m pipeline_tools --format json task validate docs/tasks/test-metrics-isolation.md` → `"status": "pass"`，exit 0。
- `python -m pipeline_tools scope check . --allowed 'tests/**' 'references/**' --task-id test-metrics-isolation` → `PASS`。
- `git status --short` 仅显示 `tests/`、`references/` 内改动（外加预存 metrics 噪声），未越界。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "test-metrics-isolation",
  "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
  "branch": "test-metrics-isolation",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_cli_suite_leaves_tracked_metrics_unchanged",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m pipeline_tools --format json task validate docs/tasks/test-metrics-isolation.md",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "executor-report.md"
    }
  ],
  "assertions": [
    "整套测试运行后仓库 .pipeline/metrics/ 未追踪文件数与总文件数均不变（4 -> 4, 1439 -> 1439）",
    "启用自动采集且不显式指定 cwd 的运行把事件写入临时 root，仓库 metrics 快照不变",
    "wrapper 用例在隔离生效时仍传播外层命令真实退出码 7",
    "references/metrics-contract.md 含真实测试隔离规则内容"
  ],
  "unverified": [],
  "evidence_refs": ["executor-report.md"],
  "identity": {
    "product_head": "14a17d2c62aa4765b53bc099af4dbb8c0e10998f"
  },
  "recommendation": "ready_for_review"
}
```