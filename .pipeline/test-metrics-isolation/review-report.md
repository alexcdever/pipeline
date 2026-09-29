# 审查报告：test-metrics-isolation

- **task-id**：test-metrics-isolation
- **worktree**：`D:\Projects\Skills\pipeline\.worktrees\test-metrics-isolation`
- **branch**：`test-metrics-isolation`
- **冻结基线**：`14a17d2c62aa4765b53bc099af4dbb8c0e10998f`
- **角色**：reviewer
- **轮次**：1
- **状态**：PASS
- **审查上下文**：独立开始，不采信执行报告；全部结论来自本轮直接读取的 diff、测试正文与我自己的重跑。

## 身份核对（先做）

| 项 | 期望 | 实测 | 结论 |
|---|---|---|---|
| task_id | test-metrics-isolation | test-metrics-isolation | 一致 |
| branch（worktree） | test-metrics-isolation | `test-metrics-isolation` | 一致 |
| worktree HEAD | 14a17d2c… | `14a17d2c62aa4765b53bc099af4dbb8c0e10998f` | 一致 |
| worktree list 配对 | main + worktree | 两条记录，路径/分支均匹配 | 一致 |
| goal.md sha256 | 9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f | 同值 | 一致 |
| 变更提交状态 | 未提交（在审状态） | `git status` 显示 M tests/test_cli.py、M tests/test_acceptance_id_and_template_compliance.py、M references/metrics-contract.md | 符合，未提交 |

无身份漂移。`git worktree list --porcelain` 显示主工作树与实现 worktree 均指向 `14a17d2c…`，配对正确。

## 真实差异（`git diff 14a17d2 -- tests/ references/`）

统计：3 文件、+113/-5，全部落在 `allowed_paths`（`tests/`、`references/`）内。

- `tests/test_cli.py`
  - 新增 `auto_metrics_requested(env)`：判断环境映射是否让自动采集保持开启（`1/true/yes/on` 视为关闭）。
  - 新增 `isolated_metrics_root()`：`tempfile.mkdtemp` 非仓库临时 root，`atexit` 清理。
  - 新增 `metrics_snapshot(directory)`：名称→内容 sha256。
  - `run_cli` 签名由 `cwd=ROOT` 改为 `cwd=None`：固定注入 `PYTHONPATH=ROOT`；当 `cwd is None` 时，启用自动采集走 `isolated_metrics_root()`，否则回退 `ROOT`。
  - 改写 wrapper 用例：改为在临时 root 内运行，并断言仓库 metrics 快照不变、隔离 root 下确有事件。
  - 新增 `test_cli_suite_leaves_tracked_metrics_unchanged`、`test_auto_metrics_enabled_run_keeps_metrics_out_of_repository`。
- `tests/test_acceptance_id_and_template_compliance.py`：新增 `test_references_metrics_contract_documents_test_isolation`，断言文档真实内容。
- `references/metrics-contract.md`：新增「测试隔离规则」一节（根因、隔离要求、`git status --short .pipeline/metrics/` 验收口径）。

## 逐条验收独立结论

| 验收 ID | 命令 | 退出码 | 我的结论 |
|---|---|---|---|
| acceptance-test-cli-suite-leaves-tracked-metrics-unchanged | `python -m unittest tests.test_cli.CLITests.test_cli_suite_leaves_tracked_metrics_unchanged` | 0 | PASS（Ran 1 test，OK） |
| acceptance-test-auto-metrics-enabled-run-isolated | `python -m unittest tests.test_cli.CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository` | 0 | PASS（Ran 1 test，OK） |
| acceptance-test-wrapper-exit-code-with-isolation | `python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code` | 0 | PASS（Ran 1 test，OK） |
| acceptance-test-metrics-contract-documents-test-isolation | `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation` | 0 | PASS（Ran 1 test，OK） |

四条验收测试独立重跑全部 exit 0，与任务单 `test_ref`/`command_ref` 逐字一致。

## 对抗性验证：核心主张（整套运行不得写受追踪 metrics）

在 worktree 内，两次快照之间不插入任何其它 `pipeline-tools` 调用：

```
BEFORE_UNTRACKED=15 BEFORE_TOTAL=1450
python -m unittest discover -s tests   → SUITE_EXIT=0
Ran 312 tests in 243.872s
OK
AFTER_UNTRACKED=15 AFTER_TOTAL=1450
```

**未追踪文件数与总文件数在整套运行前后均不变（15→15，1450→1450）。** 核心主张成立。主代理报告的 15 未追踪/1450 与我复现一致；executor 报告里的 4/1439 是它当时的不同噪声基线，不影响「无增长」这一不变量。

### 断言是否真实（非恒真）

- `test_cli_suite_leaves_tracked_metrics_unchanged`：确实对 `ROOT/.pipeline/metrics` 做名称→内容哈希快照，运行 `command run`（auto-metrics `0`/`1` 两个子例）后断言快照相等。真实比较仓库目录，不是只检查临时目录存在。
- `test_auto_metrics_enabled_run_keeps_metrics_out_of_repository`：**不传 `cwd`** 调用 `run_cli(['not-a-command'], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS':'0'})`，断言返回码 2、仓库 metrics 快照不变、隔离 root 下事件数 +1 且集合确有新增。这条真正走的是 `run_cli` 的默认 cwd 重定向路径，是隔离生效的关键证据。
- wrapper 用例：断言 `completed.returncode == 1` 且 stdout 含 `"exit_code": 7`，即外层命令真实退出码 7 在隔离生效时仍传播；同时断言仓库快照不变、隔离 root 非空。非恒真。

### 隔离触发条件与清理

- 仅在 `auto_metrics_requested(e)` 为真时，`run_cli` 才把默认 cwd 指向 `isolated_metrics_root()`；关闭自动采集时回退 `ROOT`。条件正确。
- 临时 root 由 `tempfile.mkdtemp` 生成于系统临时目录（非 Git 仓库，不在本检出内），`atexit.register(shutil.rmtree, ..., ignore_errors=True)` 清理。非仓库位置 + 有界清理，符合契约。

### `PYTHONPATH` 注入风险

`run_cli` 现将 `ROOT` 前置注入 `PYTHONPATH`，使换 cwd 后仍能 `import pipeline_tools`。核查：
- 仓库既有测试已多次显式传 `PYTHONPATH=str(ROOT)`（test_cli.py 多处、test_derived_task_dispatch_recovery.py、test_task_evidence_reconcile.py），本改动是把同一模式统一进 helper，未引入新语义。
- 未发现任何依赖 `pipeline_tools` 不可导入的测试；整套 312 测试全绿，无 ImportError 掩盖。
- 风险等级：低。未观察到行为改变。

## 非目标与范围核查

- `git diff --name-only 14a17d2` 仅三个文件：`references/metrics-contract.md`、`tests/test_acceptance_id_and_template_compliance.py`、`tests/test_cli.py`。无越界。
- `pipeline_tools/` 未改动（`git status` 无记录）。
- `.gitignore` 未改动；`.pipeline/metrics/` 仍受追踪（`git ls-files .pipeline/metrics/` = 1435 个文件；`git check-ignore --no-index .pipeline/metrics/x.json` 退出 1 = 未被忽略）。
- `docs/tasks/` 冻结任务单未改动。
- 无既有自动指标测试被跳过或删除：基线 55 个测试方法 → 工作树 57 个，新增 2 个、删除 0 个；diff 中无新增 `skip`/`Skip`。

## 证据目录

`.pipeline/test-metrics-isolation/` 仅含 `executor-report.md`、`executor-result.json`；无任何 `.log` 文件。审查前无 `review-report.md`（本轮由我创建）。

## 测试隔离文档

`references/metrics-contract.md` 新增「测试隔离规则」确实记录：根因（`_git_root(Path.cwd())`）、隔离要求（临时 root / 非仓库 cwd）、不得跳过既有测试、验收口径（`git status --short .pipeline/metrics/` 不新增未追踪文件）、与 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 的关系。文档测试断言真实内容。

**次要观察（不阻塞）**：文档测试结尾的否定断言 `assertNotIn(".pipeline/metrics/` 加入 `.gitignore`", contract)` 用的「加入」，而文档现有措辞是「加进」，该否定断言在现有文本下恒真，不构成有效反例守卫。正向内容断言是真实的，故不影响结论；可留作后续打磨。

## 未验证项

- 整套运行期间我未逐事件核对隔离临时 root 内事件内容（仅断言了事件数与集合增长）；这不影响「仓库 metrics 无增长」这一核心结论。
- 未在其它平台（非 Windows）复跑；本轮证据限于本机 Git Bash 环境。

## 建议

PASS。变更范围精确、验收四条独立通过、核心隔离主张经独立整套复现（15→15、1450→1450），无测试削弱、无越界改动。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "test-metrics-isolation",
  "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
  "branch": "test-metrics-isolation",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "git rev-parse HEAD && git branch --show-current && sha256sum goal.md",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "git diff 14a17d2 -- tests/ references/",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_cli_suite_leaves_tracked_metrics_unchanged",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\test-metrics-isolation",
      "evidence_ref": "review-report.md"
    }
  ],
  "assertions": [
    "身份一致：task-id test-metrics-isolation、branch test-metrics-isolation、worktree HEAD 14a17d2c62aa4765b53bc099af4dbb8c0e10998f、goal.md sha256 9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "diff 仅触及 tests/ 与 references/（3 文件 +113/-5），pipeline_tools/、.gitignore、docs/tasks/ 均未改动",
    "四条验收测试独立重跑全部退出码 0",
    "整套测试独立复现：Ran 312 tests / OK / exit 0；仓库 .pipeline/metrics/ 未追踪 15->15、总数 1450->1450，无增长",
    "未删除或跳过既有自动指标测试：55 -> 57 个测试方法，新增 2、删除 0，diff 无 skip",
    "隔离仅在自动采集开启时触发，临时 root 位于非仓库系统临时目录并由 atexit 清理",
    ".pipeline/test-metrics-isolation/ 仅含 executor-report.md 与 executor-result.json，无 .log",
    ".pipeline/metrics/ 仍受追踪（1435 个 tracked 文件，check-ignore 退出 1），未被加入 .gitignore"
  ],
  "evidence_refs": [
    "review-report.md",
    "reviewer-result.json"
  ],
  "unverified": [
    "未逐事件核对隔离临时 root 内事件内容（仅核验事件数与集合增长）",
    "未在非 Windows 平台复跑"
  ],
  "identity": {
    "product_head": "14a17d2c62aa4765b53bc099af4dbb8c0e10998f"
  },
  "recommendation": "merge"
}
```
