# 执行报告：metrics-tracking-policy-continuation-1

- task-id：`metrics-tracking-policy-continuation-1`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\metrics-tracking-policy-continuation-1`
- branch：`metrics-tracking-policy-continuation-1`
- 角色：executor
- 轮次：1
- 基线 HEAD：`dd1e74916a4374eb0eabbc69cc13a29805bb65fd`
- 产品 HEAD（报告时，改动未提交）：`dd1e74916a4374eb0eabbc69cc13a29805bb65fd`
- goal sha256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`（与契约一致）

## 改动摘要

父任务 `metrics-tracking-policy` 已移除「`.pipeline/metrics/` 必须纳入 Git」的强制，策略改为：**追踪与否由项目开发者决定，技能既不要求也不禁止**。`README.md` 当时不在父任务允许范围内，仍保留三处旧强制措辞。本任务把这三处改写为中性表述，并新增一个守护测试。

### 逐处 before / after

**1) 第 16 行（默认项目约定）**

before：
`- 项目级统计：\`.pipeline/metrics/\`（由工具自动生成并纳入 Git 追踪）`

after：
`- 项目级统计：\`.pipeline/metrics/\`（由工具自动生成；是否纳入 Git 由项目开发者决定）`

**2) 「项目级反馈」段（原 63-66 行）**

before：
```
除 `metrics` 子命令外，所有 `pipeline-tools` 阶段命令默认自动记录一个结构化指标事件到
目标项目的 `.pipeline/metrics/`。指标文件是可审查的流水线历史，应纳入 Git；不要把该目录
加入项目的 `.gitignore`。自动采集只使用命令退出码、结构化结果和可定位的证据路径，不会从
自然语言报告推断产品结论，也不会记录 token、凭据、完整命令输出或业务数据。
```

after：
```
除 `metrics` 子命令外，所有 `pipeline-tools` 阶段命令默认自动记录一个结构化指标事件到
目标项目的 `.pipeline/metrics/`。该目录由工具自动创建和写入；是否把它纳入 Git 由项目开发者
决定，技能既不要求也不禁止（本仓库把 `.pipeline/metrics/` 加入了 `.gitignore`）。自动采集
只使用命令退出码、结构化结果和可定位的证据路径，不会从自然语言报告推断产品结论，也不会
记录 token、凭据、完整命令输出或业务数据。
```

**3) 第 96 行（进度日志对比句）**

before（片段）：
`…不进入 Git；\`.pipeline/metrics/\` 的指标事件则相反，应纳入 Git。正式 \`evidence verify\`…`

after（片段）：
`…不进入 Git；\`.pipeline/metrics/\` 的指标事件不受这条规则约束，是否纳入 Git 由项目开发者决定（本仓库把 \`.pipeline/metrics/\` 加入了 \`.gitignore\`）。正式 \`evidence verify\`…`

**保留不变**：进度日志规则原文（`.pipeline/*/*-progress.jsonl` 由 `.gitignore` 排除、不进入 Git）完整保留。

## 新增测试

`tests/test_acceptance_id_and_template_compliance.py` 的 `AcceptanceIdAndTemplateComplianceTests` 新增唯一方法 `test_readme_documents_metrics_tracking_is_developer_choice`（文件第 400-414 行）。断言：

- 正向：`README.md` 含 `由项目开发者决定`、`技能既不要求也不禁止`，且进度日志规则仍在（含 `.pipeline/*/*-progress.jsonl`、`不进入 Git`）。
- 负向：`纳入 Git 追踪`、`应纳入 Git`、`不要把该目录`、`加入项目的` 均不在 README 中。

### 非重言证据（负向断言针对的是改动前真实存在的字符串）

对 `git show HEAD:README.md`（改动前）逐串检查：

| 断言缺失的字符串 | 改动前是否存在于 README | 改动后 |
|---|---|---|
| `纳入 Git 追踪` | True（原第 16 行） | 0 次 |
| `应纳入 Git` | True（原第 64、96 行） | 0 次 |
| `不要把该目录` | True（原第 64 行） | 0 次 |
| `加入项目的` | True（原第 65 行） | 0 次 |
| `由项目开发者决定`（正向） | False | 存在（2 处） |

因此负向断言不是恒真：若策略回归（重新写入旧强制措辞），测试会失败。

## 命令与结果

| 命令 | cwd | 退出码 | 结果 |
|---|---|---|---|
| `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_readme_documents_metrics_tracking_is_developer_choice` | worktree | 0 | Ran 1 test … OK |
| `python -m unittest discover -s tests` | worktree | 0 | Ran 317 tests … OK（基线 316 + 新增 1） |
| `python -m pipeline_tools --format json task validate docs/tasks/metrics-tracking-policy-continuation-1.md` | worktree | 0 | `"status": "pass"` |
| `git status --short` | worktree | 0 | 仅 `README.md`、`tests/test_acceptance_id_and_template_compliance.py` 修改 |

一次性 scratch（`git show HEAD:README.md` 对比）也用于非重言证据；首次因 Windows 下 `/tmp` 解析失败退出 1，改用仓库内临时文件后退出 0，临时文件已删除。

## 未验证项

- 未在合并后的主工作树复验（本任务范围内不合并；主代理负责）。
- 未检查 `README.md` 之外是否有其它文档仍复述旧强制措辞（契约中 `unknown-other-docs-restate-mandate`，非阻塞，且仅 `README.md`、`tests/` 在允许范围内）。
- 改动未提交（按契约要求保留现场，由主代理提交与合并）。

## 建议

`PASS` —— README 三处旧措辞已与父任务新策略对齐，进度日志规则完好，新增守护测试可真实回归失败，全套 317 项测试通过。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "metrics-tracking-policy-continuation-1",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\metrics-tracking-policy-continuation-1",
  "branch": "metrics-tracking-policy-continuation-1",
  "identity": {
    "product_head": "dd1e74916a4374eb0eabbc69cc13a29805bb65fd",
    "goal_sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f"
  },
  "evidence_refs": [
    "executor-report.md",
    "executor-result.json"
  ],
  "commands": [
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_readme_documents_metrics_tracking_is_developer_choice",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\metrics-tracking-policy-continuation-1",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\metrics-tracking-policy-continuation-1",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m pipeline_tools --format json task validate docs/tasks/metrics-tracking-policy-continuation-1.md",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\metrics-tracking-policy-continuation-1",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "git show HEAD:README.md > .tmp-readme-head.md && python -c \"...scan stale strings...\" && rm -f .tmp-readme-head.md",
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\metrics-tracking-policy-continuation-1",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    }
  ],
  "assertions": [
    "README.md 的三处旧强制追踪措辞已替换为开发者自决表述",
    "README.md 仍保留进度日志不进入 Git 的规则",
    "新增测试的负向断言针对改动前确实存在的字符串，非恒真",
    "全量测试 317 通过，基线 316 之上仅新增 1"
  ],
  "unverified": [
    "post-merge re-verification in the main worktree (out of scope for the executor)",
    "whether any doc other than README.md restates the removed mandate"
  ],
  "recommendation": "pass"
}
```