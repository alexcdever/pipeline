# metrics-tracking-policy — 主代理最终检查

- task-id：`metrics-tracking-policy`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy`
- branch：`metrics-tracking-policy`
- role：main-final（第三层验证）
- 冻结基线 HEAD：`776d3d9609703b2220e0ed0856dc940de15a88cc`
- 结论：**PASS**

## 1. 身份与现场核对

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| task_id | `metrics-tracking-policy` | 任务单与证据身份字段 | 一致 |
| branch | `metrics-tracking-policy` | `git branch --show-current` | 一致 |
| worktree | `.worktrees/metrics-tracking-policy` | `git worktree list` | 一致 |
| 冻结基线 | `776d3d9…` | `git rev-parse HEAD` | 一致 |
| goal sha256 | `9abb196a…086e25f` | `sha256sum goal.md` | 一致 |
| 冻结任务单未被改动 | 期望无 diff | `git diff --name-only HEAD -- docs/` 为空 | 一致 |

**证据目录归属已澄清**：本任务的证据写入主仓库 `.pipeline/metrics-tracking-policy/`（该目录含 `executor-result.json`，pre-merge gate 以此为准）。审查子代理一度在工作树内也复制了一份 review 报告，属重复；主仓库那份为权威。

## 2. 三份报告与机器结果

`.pipeline/metrics-tracking-policy/` 含 `executor-report.md`、`review-report.md`、`final-check.md`、
`executor-result.json`、`reviewer-result.json`、`final-result.json`。无 `.log`、无 `.jsonl`。
markdown 侧 `status` 为大写 `PASS`；JSON 侧 `status` 为小写 `pass`。三份报告各含恰好一个 `pipeline-evidence` 块。

## 3. 独立重跑关键验收（主代理亲自执行）

| 验收 ID | 退出码 |
|---|---|
| acceptance-test-metrics-contract-tracking-optional | 0 |
| acceptance-test-compat-doc-tracking-optional | 0 |
| acceptance-test-repo-metrics-untracked-and-ignored | 0 |
| acceptance-test-suite-metrics-isolation-without-tracking | 0 |

全量测试主代理独立复跑：`python -m unittest discover -s tests` → **Ran 316 tests … OK**，退出码 0（基线 312，新增 4，无回归）。

## 4. 抽查高风险断言（亲自阅读 diff，未依赖子代理转述）

- `references/metrics-contract.md`：开头「应纳入 Git 追踪，不应加入项目 .gitignore」已替换为开发者自决原则；「进度日志不进入 Git」一节的对照句已中性化；「测试隔离规则」改为与追踪状态无关，明确「判定基准是仓库目录的实际内容，不依赖 Git 追踪状态」。**进度日志规则完整保留。**
- `references/compat-and-migration.md`：两处「必须纳入 Git 追踪」已中性化。
- `.gitignore`：新增 `.pipeline/metrics/`。
- `tests/test_cli.py`：`check-ignore --no-index` 的断言由「必须不被忽略」改为「忽略与否均可」（`assertIn(returncode,(0,1))`）；新增 `test_repository_metrics_are_ignored_and_untracked`（读真实仓库根：`.gitignore` 含规则、`check-ignore` 返回 0、`ls-files` 为空）与 `test_cli_suite_does_not_write_repository_metrics`（对仓库 metrics 目录做内容哈希快照，跑真实启用采集的 CLI 调用，断言快照不变）。隔离断言改为直接测量目录内容，不再用 `git status`。
- `tests/test_acceptance_id_and_template_compliance.py`：恒真断言 `assertNotIn(".pipeline/metrics/` 加入 `.gitignore`")`（文档实为 `加进`，永不失败）已替换为正向断言；新增两条开发者自决契约测试，包含对旧措辞的 `assertNotIn`。

## 5. untrack 的非破坏性（本任务核心）

- `git ls-files .pipeline/metrics/` → **0**（已全部移出索引）。
- `git check-ignore -v .pipeline/metrics/event.json` → 命中 `.gitignore:7`。
- 磁盘文件仍在：`find .pipeline/metrics -type f` 计数 > 0。
- 审查子代理用「HEAD 树 blob 哈希 vs 磁盘 `git hash-object`」逐一比对 1435 条路径 → **mismatch=0，missing=0**，无任何既有文件被删改；磁盘多出的名字是本轮工具自身追加的事件，非删除。

## 6. 范围与非目标

`git diff --name-only HEAD`（排除 metrics 删除）仅 `references/`、`tests/`、`.gitignore`，全在 `allowed_paths` 内。`pipeline_tools/`、`docs/tasks/` 未改动。

**关于 `forbidden_paths` 的 `.pipeline/** existing history` 与 1435 条 staged 删除**：该 prose 模式经 `pipeline_tools/core.py` 的 `_matches` 判定**不匹配**（它以 `history` 结尾而非 `/**`），且 `scope_check` 对 metrics 路径豁免；实测 `scope check` 对该状态返回 PASS。内容经哈希比对证明完好，故「不得改写既有证据内容」的意图成立。staged 删除是**本任务预期的交付物**，非契约违反。

## 7. 未验证项与需裁决项

- **README 不一致（真实、需另开 `derived` 单）**：`README.md` 至少第 16、64、96 行仍称 `.pipeline/metrics/` 应纳入 Git 追踪，与新 `.gitignore` 及本任务改后的 `references/` 相矛盾。`README.md` 不在 `allowed_paths`，故本任务未动，**不得**借此扩大本冻结契约范围。建议开 `derived` 任务（id/path 保留 `continuation`，`allowed_paths` 覆盖 `README.md`）修正。
- **执行报告措辞不准确（已记录，不采信其原话）**：执行报告称 `test_cli_suite_leaves_tracked_metrics_unchanged` 被「删除/改名」，实际 diff 未如此——该测试与其同伴仍存在，且因改用内容哈希仍有意义，仅名字是过时的误称。审查子代理已独立指出。
- **`commit_history_check` / `scope history`**：交付物提交前无法对历史扫描，合并后在主工作树复验时补。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "metrics-tracking-policy",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy",
  "branch": "metrics-tracking-policy",
  "role": "main-final",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_repository_metrics_are_ignored_and_untracked",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_cli_suite_does_not_write_repository_metrics",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy",
      "evidence_ref": "final-check.md"
    }
  ],
  "assertions": [
    "4 条验收测试由主代理亲自重跑，退出码全为 0",
    "全量 316 tests OK，基线 312 之上仅新增 4，无回归",
    "untrack 非破坏：ls-files=0、check-ignore 命中、磁盘文件保留；审查子代理以 blob 哈希逐一比对 1435 条路径 mismatch=0 missing=0",
    "生产 diff 由主代理直接阅读：仅 references/、tests/、.gitignore，全在 allowed_paths",
    "进度日志规则完整保留；旧强制追踪措辞已从 references/ 清除",
    "恒真断言已替换为可失败的正向断言",
    "staged metrics 删除经 _matches 与 scope_check 判定非契约违反，内容完好"
  ],
  "evidence_refs": ["final-check.md", "executor-report.md", "review-report.md"],
  "unverified": [
    "README.md 第 16/64/96 行仍称 metrics 应追踪，与新政矛盾，需另开 derived 任务",
    "commit_history_check / scope history 需在提交后补跑",
    "执行报告关于测试被删除/改名的措辞不准确，不予采信"
  ],
  "recommendation": "ready_to_merge"
}
```
