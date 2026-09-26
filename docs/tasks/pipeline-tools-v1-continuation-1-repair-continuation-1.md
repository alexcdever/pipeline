# pipeline-tools-v1 continuation-1 repair continuation-1：收口指标身份、脱敏与失败保护

<!-- Task ID: pipeline-tools-v1-continuation-1-repair-continuation-1 -->
<!-- Parent history is retained unchanged. This continuation records only repair work and current evidence. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "pipeline-tools-v1-continuation-1-repair-continuation-1",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "docs/tasks/pipeline-tools-v1-continuation-1-repair-continuation-1.md",
    "pipeline_tools/__main__.py",
    "pipeline_tools/core.py",
    "tests/test_cli.py",
    "tests/test_metrics.py",
    "tests/test_git_checks.py",
    ".gitignore",
    ".pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/**"
  ],
  "forbidden_paths": [
    "implement-plan.md",
    "IDEA.md",
    "docs/tasks/pipeline-tools-v1.md",
    "docs/tasks/pipeline-tools-v1-continuation-1.md",
    ".pipeline/pipeline-tools-v1-continuation-1/**",
    "**/.env",
    "**/*secret*",
    "package.json",
    "pnpm-lock.yaml"
  ],
  "operations": [
    {
      "id": "repair-metric-boundary",
      "kind": "code-and-regression-tests",
      "scope": "unify metric_event identifier/path redaction and preserve retry attempt identity",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2"]
    },
    {
      "id": "repair-cli-attribution",
      "kind": "code-and-regression-tests",
      "scope": "close automatic attribution for malformed/help/runtime/lifecycle/relative-log invocations without changing original exit codes",
      "acceptance_tests": ["acceptance-test-3", "acceptance-test-4"]
    },
    {
      "id": "repair-policy-boundary",
      "kind": "policy-and-scope-regression-tests",
      "scope": "retain export ignore policy and prove metrics exemption cannot override forbidden or tracked changes",
      "acceptance_tests": ["acceptance-test-5"]
    },
    {
      "id": "repair-regression",
      "kind": "full-regression",
      "scope": "run the complete Python test suite and validate this continuation sheet",
      "acceptance_tests": ["acceptance-test-6"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py", "pipeline_tools/core.py"],
    "interaction": ["CLI argument parsing and automatic metric finalization"],
    "application": ["automatic observed/derived metric event construction"],
    "domain": ["task/run/terminal/evidence identity and no-sensitive-data boundary"],
    "persistence": [".pipeline/metrics/*.json"],
    "readback": ["tests/test_cli.py", "tests/test_metrics.py"],
    "recovery": ["original command exit code remains authoritative when metric attribution/write fails"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 1,
      "test_ref": "tests/test_metrics.py: test_metric_event_redacts_full_sensitive_vocabulary_and_absolute_path_identifiers",
      "command_ref": "python -m unittest tests.test_metrics.MetricsTests.test_metric_event_redacts_full_sensitive_vocabulary_and_absolute_path_identifiers"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 1,
      "test_ref": "tests/test_cli.py: test_automatic_retry_preserves_attempt_and_reason_for_first_retry",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_automatic_retry_preserves_attempt_and_reason_for_first_retry"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 1,
      "test_ref": "tests/test_cli.py: test_unknown_top_level_and_help_invocations_record_automatic_metrics",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_unknown_top_level_and_help_invocations_record_automatic_metrics"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 1,
      "test_ref": "tests/test_cli.py: test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity; test_automatic_command_uses_task_id_from_workflow_log_path",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity tests.test_cli.CLITests.test_automatic_command_uses_task_id_from_workflow_log_path"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: test_forbidden_metrics_pattern_still_wins and test_tracked_metrics_are_workflow_metadata",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_forbidden_metrics_pattern_still_wins tests.test_git_checks.GitChecks.test_tracked_metrics_are_workflow_metadata"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 1,
      "test_ref": "tests/: complete regression suite and continuation contract validation",
      "command_ref": "python -m unittest discover -s tests -v && python -m pipeline_tools task validate docs/tasks/pipeline-tools-v1-continuation-1-repair-continuation-1.md"
    }
  ],
  "dependencies": ["pipeline-tools-v1-continuation-1 (historical parent; retained, not rewritten)"],
  "required_evidence_levels": [1, 2]
}
```

## 任务身份

- 项目：programing-pipeline（内置 `pipeline_tools`）
- 领域或阶段：pipeline-tools v1 continuation-1 repair
- 用户结果或系统能力：修复 review reports 中尚未收口的 P1/P2 缺口，并以当前测试证明自动指标身份、脱敏、失败保护和 Git 范围边界。
- 父任务：`pipeline-tools-v1-continuation-1`；父任务报告与历史 metrics 不改写。
- 执行 worktree 约定：`<仓库根目录>/.worktrees/pipeline-tools-v1-continuation-1-repair-continuation-1`
- 状态：未开始

## 依赖与范围

### 前置条件

- 父任务及其 review reports 已读取；本 continuation 只修复明确列出的缺口。

### 已读取的父任务缺口分类

- 已由当前测试覆盖、无需重复修复：已识别 malformed recognized-group 记录、top-level parse error、retry attempt=1、runtime/lifecycle evidence identity、relative command log evidence reference、scope forbidden precedence、extended sensitive path checks（见父任务当前 `tests/test_cli.py` 与 `tests/test_git_checks.py`）。这些只作为回归保留。
- 未修复/本任务收口：`metric_event` 仍未统一完整 credential vocabulary/absolute-path-shaped identifiers；help/unknown non-metrics coverage需闭环；automatic metric finalization/write failures需有 bounded diagnostic 且保持原退出码；retry derived event需保持 attempt/reason；父任务/continuation policy conflict保留历史并由本任务明确只保留 export ignore；当前证据 ledger 不在父任务上改写。
- 环境缺口：历史 reviewer 因 pnpm 9.15.4 不可用而 BLOCKED；本 repair 的 Python 测试不把历史 reviewer 报告当 PASS，当前执行/审查证据单独记录。

### 允许修改

- `pipeline_tools/__main__.py`、`pipeline_tools/core.py`。
- 现有 `tests/test_cli.py`、`tests/test_metrics.py`、必要的 `tests/test_git_checks.py` 回归用例。
- `.gitignore` 仅保留 `.pipeline/metrics-export.json` 忽略规则并使事件目录可追踪。
- 本 continuation task sheet 与其 `.pipeline` 证据。

### 明确不改

- 不改 `implement-plan.md`、`IDEA.md`、父任务 task sheet、父任务 reports、历史 metrics 或父任务证据目录。
- 不改产品接口的退出码语义；自动采集失败不得替换原命令退出码。
- 不记录 prompt、完整日志、凭据、token 或业务数据；不新增依赖；不联网。

## 事实、假设与待决

### 已确认事实

- 父任务 `pipeline-tools-v1-continuation-1` 的 review/re-review/final review 均保留在原目录，且结论为 BLOCKED；本任务不把历史报告升级为 PASS。
- 当前主工作树已有针对部分 P1/P2 的测试覆盖；未覆盖项在上方分类中列明。

### 未验证事实

- 本 repair 代码修改及独立 review 尚未完成。
- pnpm 版本环境不属于本 Python repair 的验收前置，历史 reviewer 阻塞仍未改变。

### 禁止猜测

- 不以历史 full-test 日志替代本任务的当前证据；不将测试数量或旧报告结论当作修复证明。

## 设计与行为契约

任意非 `metrics` CLI 调用（包括 argparse 错误与 help）
→ 自动采集从 argv 做最佳努力机械归因，无法安全归因时使用 unknown
→ 写入脱敏 observed/derived 事件，写入失败只追加 bounded diagnostic/not-collected signal且不递归
→ 原命令退出码、task/run/terminal/evidence 身份保持权威
→ 指标边界拒绝/归一化 credential-looking identifiers、绝对路径形状和敏感 evidence components。

## 验收测试

### 验收测试1：指标边界统一脱敏

- 触发：写入包含 authorization/passwd/bearer/cvc 或绝对路径形状的 metric event。
- 断言：task_id/reason 归一为 unknown，敏感 evidence_ref 归一为 null，绝对路径不落盘。
- 测试：`tests/test_metrics.py: test_metric_event_redacts_full_sensitive_vocabulary_and_absolute_path_identifiers`
- 命令：`python -m unittest tests.test_metrics.MetricsTests.test_metric_event_redacts_full_sensitive_vocabulary_and_absolute_path_identifiers`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0，单测在 180 秒内完成。

### 验收测试2：重试身份保持

- 触发：以 `--attempt 1` 执行 command run。
- 断言：observed 与 derived retry 事件均保留 `attempt=1` 和 `reason=attempt_1`。
- 测试：`tests/test_cli.py: test_automatic_retry_records_first_retry_attempt`
- 命令：`python -m unittest tests.test_cli.CLITests.test_automatic_retry_records_first_retry_attempt`
- 验收模式：集成
- 证据等级：1
- 结果要求：退出码 0，临时项目隔离且 180 秒内完成。

### 验收测试3：未知与 help 调用归因

- 触发：调用未知顶层命令与非 metrics help。
- 断言：原始 argparse 退出码保持不变，并生成 cli_parse_error/cli_help 自动事件。
- 测试：`tests/test_cli.py: test_top_level_parse_error_records_a_failure_metric; test_subcommand_help_records_a_help_metric`
- 命令：`python -m unittest tests.test_cli.CLITests.test_top_level_parse_error_records_a_failure_metric tests.test_cli.CLITests.test_subcommand_help_records_a_help_metric`
- 验收模式：集成
- 证据等级：1
- 结果要求：退出码与断言匹配，180 秒内完成。

### 验收测试4：失败保护与相对日志身份

- 触发：自动 metric 归因/写入异常及 cwd 外执行相对 log。
- 断言：原始 command exit code 不被替换；task/evidence identity 从 `--cwd` 正确解析。
- 测试：`tests/test_cli.py: test_automatic_command_uses_task_id_from_workflow_log_path; test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity`
- 命令：`python -m unittest tests.test_cli.CLITests.test_automatic_command_uses_task_id_from_workflow_log_path tests.test_cli.CLITests.test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity`
- 验收模式：集成
- 证据等级：1
- 结果要求：退出码 0，故障诊断有界且 180 秒内完成。

### 验收测试5：Git metrics policy scope

- 触发：scope check 遇 metrics 生成/跟踪/禁止 pattern。
- 断言：允许的 metrics workflow metadata 不产生 drift，显式 forbidden 仍优先；export 文件保持 ignored。
- 测试：`tests/test_git_checks.py: test_forbidden_metrics_pattern_still_wins; test_tracked_metrics_are_workflow_metadata`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_forbidden_metrics_pattern_still_wins tests.test_git_checks.GitChecks.test_tracked_metrics_are_workflow_metadata`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0，180 秒内完成。

### 验收测试6：完整回归与任务单结构

- 触发：执行全量测试并验证本 schema2 task sheet。
- 断言：全部测试通过，任务单结构校验通过；失败保留原始日志，不宣称 PASS。
- 测试：`tests/: complete regression suite; pipeline_tools task validate`
- 命令：`python -m unittest discover -s tests -v && python -m pipeline_tools --format json task validate docs/tasks/pipeline-tools-v1-continuation-1-repair-continuation-1.md`
- 验收模式：集成
- 证据等级：1
- 结果要求：整套命令累计不超过 300 秒，退出码 0。

## 环境前置

1. Python 3.11+，从仓库根目录运行 `python -m unittest` 和 `python -m pipeline_tools`。
2. 每条验收命令默认 180 秒上限；测试使用临时 Git/project 目录。
3. 不要求 pnpm；历史 pnpm handshake BLOCKED 保留为父任务事实，不被本任务改写。

## 决策点

1. 若修复要求改写父任务 contract/report/metrics，停止并建立新的 continuation，不覆盖历史。
2. 若自动指标无法安全脱敏或归因，保留 unknown/null 并报告 BLOCKED，不猜测。
3. 若测试环境缺失 Python 或 Git，保留证据现场，不把环境阻塞写成产品 PASS。

---

## 任务级进度（主代理维护）

### 任务锚点

- 基线 HEAD：-
- 契约提交：-
- 执行分支：-
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/pipeline-tools-v1-continuation-1-repair-continuation-1`

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-1 | 未开始 | - | - | - |
| acceptance-test-2 | 未开始 | - | - | - |
| acceptance-test-3 | 未开始 | - | - | - |
| acceptance-test-4 | 未开始 | - | - | - |
| acceptance-test-5 | 未开始 | - | - | - |
| acceptance-test-6 | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| - | 任务单创建 | 未开始 | - | validate、提交契约、创建唯一 worktree |

### 设计变更与延续任务索引

- 父任务：`docs/tasks/pipeline-tools-v1-continuation-1.md`（保留历史，未改写）。
- 无新的延续任务。

### 最终结果

- 状态：未开始
- 执行子代理：未开始
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：-
- 合并后复验：未开始
- 遗留项：-
