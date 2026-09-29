# metrics-tracking-policy-continuation-1 — 主代理最终检查

- task-id：`metrics-tracking-policy-continuation-1`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy-continuation-1`
- branch：`metrics-tracking-policy-continuation-1`
- role：main-final（第三层验证）
- 冻结基线 HEAD：`dd1e74916a4374eb0eabbc69cc13a29805bb65fd`
- 结论：**PASS**

## 1. 身份与现场核对

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| task_id | `metrics-tracking-policy-continuation-1` | 任务单与证据身份字段 | 一致 |
| branch | `metrics-tracking-policy-continuation-1` | `git branch --show-current` | 一致 |
| worktree | `.worktrees/metrics-tracking-policy-continuation-1` | `git worktree list` | 一致 |
| 冻结基线 | `dd1e749…` | `git rev-parse HEAD` | 一致 |
| goal sha256 | `9abb196a…086e25f` | `sha256sum goal.md` | 一致 |
| 冻结任务单未被改动 | 期望无 diff | `git diff --name-only HEAD -- docs/` 为空 | 一致 |

## 2. 三份报告与机器结果

`.pipeline/metrics-tracking-policy-continuation-1/`（worktree）含 `executor-report.md`、`review-report.md`、`final-check.md`、`executor-result.json`、`reviewer-result.json`、`final-result.json`。无 `.log`、无 `.jsonl`。markdown 侧 `status` 大写 `PASS`；JSON 侧小写 `pass`。三份报告各含恰好一个 `pipeline-evidence` 块。

**证据目录归拢说明**：执行者把证据写进主仓库 `.pipeline/metrics-tracking-policy-continuation-1/`，审查者写进 worktree 同名目录。因 pre-merge gate 要求三份机器结果同处一目录、且新测试只存在于 worktree，主代理已把执行者的两份复制到 worktree 证据目录，形成单一权威目录。主仓库副本保留不删。

## 3. 独立重跑关键验收（主代理亲自执行）

| 验收 ID | 退出码 |
|---|---|
| acceptance-test-readme-documents-tracking-is-developer-choice | 0 |

全量测试主代理独立复跑：`python -m unittest discover -s tests` → **Ran 317 tests … OK**，退出码 0（基线 316，新增 1，无回归）。

## 4. 抽查高风险断言（亲自阅读 diff）

`README.md` 三处旧强制措辞已全部替换为开发者自决表述：

| 位置 | 改前 | 改后 |
|---|---|---|
| 第 16 行 | `（由工具自动生成并纳入 Git 追踪）` | `（由工具自动生成；是否纳入 Git 由项目开发者决定）` |
| 项目级反馈节 | `应纳入 Git；不要把该目录加入项目的 .gitignore。` | `该目录由工具自动创建和写入；是否把它纳入 Git 由项目开发者决定，技能既不要求也不禁止（本仓库把 .pipeline/metrics/ 加入了 .gitignore）。` |
| 第 96 行 | `则相反，应纳入 Git。` | `不受这条规则约束，是否纳入 Git 由项目开发者决定（本仓库把 .pipeline/metrics/ 加入了 .gitignore）。` |

**进度日志规则完整保留**：`README.md` 仍写明 `.pipeline/*/*-progress.jsonl` 由 `.gitignore` 排除、不进入 Git。

## 5. 负向断言非恒真（本任务最容易出问题之处）

新增测试 `test_readme_documents_metrics_tracking_is_developer_choice` 对四条字符串做 `assertNotIn`。主代理亲自对照 `git show HEAD:README.md` 逐条验证它们在**改动前确实存在**：

| 断言缺失串 | 改动前次数 | 改动后次数 |
|---|---|---|
| `纳入 Git 追踪` | 1 | 0 |
| `应纳入 Git` | 2 | 0 |
| `不要把该目录` | 1 | 0 |
| `加入项目的` | 1 | 0 |

四条全部非恒真。审查子代理另做了注入探针，确认双向敏感（重新插入任一条 → 失败）。**这是本仓库此前踩过的坑（恒真断言），本任务未重蹈。**

## 6. 范围与非目标

`git diff --name-only HEAD` 仅 `README.md`、`tests/test_acceptance_id_and_template_compliance.py`，全在 `allowed_paths`。`pipeline_tools/`、`docs/tasks/`、`references/`、`.gitignore` 未改动。

## 7. 未验证项与遗留

- **历史报告中的既有乱码**：`.pipeline/evidence-retention-forward-gate/executor-report.md` 与 `.pipeline/gate-deletion-semantics/executor-report.md` 各含 2 个 U+FFFD。属已入库历史（`forbidden_paths` 覆盖），本任务不动，登记为可选清理项。
- 合同未知项 `unknown-other-docs-restate-mandate`（非阻塞）：README 之外是否还有文档复述旧强制，未在本任务范围核查。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "metrics-tracking-policy-continuation-1",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy-continuation-1",
  "branch": "metrics-tracking-policy-continuation-1",
  "role": "main-final",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_readme_documents_metrics_tracking_is_developer_choice",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy-continuation-1",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy-continuation-1",
      "evidence_ref": "final-check.md"
    }
  ],
  "assertions": [
    "验收测试由主代理亲自重跑，退出码 0",
    "全量 317 tests OK，基线 316 之上仅新增 1，无回归",
    "README 三处旧强制措辞已替换为开发者自决表述，进度日志规则保留",
    "四条负向断言经对照 HEAD 版 README 证明改动前确实存在，非恒真",
    "生产 diff 仅 README.md 与 tests/，全在 allowed_paths",
    "证据目录无 .log/.jsonl，报告无 U+FFFD，三份报告各含恰好一个 pipeline-evidence 块"
  ],
  "evidence_refs": ["final-check.md", "executor-report.md", "review-report.md"],
  "unverified": [
    "README 之外是否还有文档复述旧强制（合同非阻塞未知项）",
    "两个历史证据报告各含 2 个 U+FFFD，属已入库历史，本任务未清理"
  ],
  "recommendation": "ready_to_merge"
}
```