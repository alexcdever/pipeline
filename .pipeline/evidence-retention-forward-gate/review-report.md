# 审查者报告：evidence-retention-forward-gate

```pipeline-evidence
{
  "schema": 1,
  "task_id": "evidence-retention-forward-gate",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/evidence-retention-forward-gate",
  "branch": "evidence-retention-forward-gate",
  "role": "reviewer",
  "round": 1,
  "status": "PASS_WITH_CONDITIONS",
  "commands": [
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_keeps_exactly_the_documented_retained_names", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_tracked_pipeline_evidence_contains_only_retained_names", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_scope_history_since_baseline_ignores_earlier_violations", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_scope_history_cli_since_passes_baseline_and_reports_drift", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_evidence_retention_contract_matches_forward_gate", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_tracked_metrics_are_workflow_metadata tests.test_git_checks.GitChecks.test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_validate_task_sheet_script_accepts_schema4_sheet", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generated_schema4_forbidden_paths_do_not_contradict_task_scope", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python scripts/validate_task_sheet.py docs/tasks/evidence-retention-forward-gate.md", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline", "exit_code": 4},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline --since d238ba2", "exit_code": 0},
    {"command": "GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0}
  ],
  "assertions": [
    "87 个删除文件全部不在 7 个保留名内，且无 .pipeline/metrics/ 文件被删",
    "commit_history_check 新增 since 参数，revision_range = f'{since}..HEAD' if since else '--all'；RETAINED_EVIDENCE_NAMES 单点定义且被 finalize_evidence 复用",
    "scope history --since 为前向闸门；--since d238ba2（清理提交）后 exit 0 PASS，默认全量扫描 exit 4",
    "references/compat-and-migration.md 的冲突句已删除，7 个保留文件明文契约写入 acceptance-evidence.md 与 metrics-contract.md",
    "scripts/validate_task_sheet.py 支持 schema 4，实跑本任务单 exit 0",
    "planning._task_forbidden_paths 对触及 .pipeline/ 的任务不再写 .pipeline/** existing history",
    "验收测试 7 方法 B 已补本地 git identity，剥离全局 identity 后仍 exit 0"
  ],
  "evidence_refs": ["review-report.md", "reviewer-result.json"],
  "unverified": ["合并到 main", "主代理终审 final-check", "11 个超范围删除的终审裁决"]
}
```

本报告只记录本轮由审查者直接运行或读取的结果。未直接观察的内容列入 `unverified`。所有命令均在 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 下运行。

## 一、身份核对

- task-id：`evidence-retention-forward-gate`，与目录名一致。
- worktree：`D:/Projects/Skills/pipeline/.worktrees/evidence-retention-forward-gate`。
- branch：`evidence-retention-forward-gate`。
- 基线：`cdf55e9`（`Freeze generated task evidence-retention-forward-gate`）。
- 提交顺序（`git log --oneline -5`）：`c27b7c7` → `d238ba2` → `cdf55e9`，正确���
- 本报告生成时的 HEAD：`c27b7c7a2a04f9549db02f70b588a8e5d3b401dd`。

## 二、逐条验收测试的独立验证

| # | 验收测试 id | 独立运行命令（前缀 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest `） | exit | 判定 |
| --- | --- | --- | --- | --- |
| 1 | acceptance-test-retained-evidence-contract | `tests.test_git_checks.GitChecks.test_commit_history_check_keeps_exactly_the_documented_retained_names` | 0 | PASS |
| 2 | acceptance-test-repository-evidence-only-retained | `tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_tracked_pipeline_evidence_contains_only_retained_names` | 0 | PASS |
| 3 | acceptance-test-since-baseline-ignores-earlier-history | `tests.test_git_checks.GitChecks.test_scope_history_since_baseline_ignores_earlier_violations` | 0 | PASS |
| 4 | acceptance-test-default-history-scan-unchanged | `tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard` | 0 | PASS |
| 5 | acceptance-test-scope-history-cli-since | `tests.test_cli.CLITests.test_scope_history_cli_since_passes_baseline_and_reports_drift` | 0 | PASS |
| 6 | acceptance-test-references-evidence-contract-aligned | `tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_evidence_retention_contract_matches_forward_gate` | 0 | PASS |
| 7 | acceptance-test-metrics-tracked-not-ignored | `tests.test_git_checks.GitChecks.test_tracked_metrics_are_workflow_metadata tests.test_git_checks.GitChecks.test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt` | 0（`Ran 2 tests`，OK） | PASS |
| 8 | acceptance-test-task-sheet-script-schema4 | `tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_validate_task_sheet_script_accepts_schema4_sheet` | 0 | PASS |
| 9 | acceptance-test-forbidden-paths-scope-consistent | `tests.test_task_generation.TaskGenerationTests.test_generated_schema4_forbidden_paths_do_not_contradict_task_scope` | 0 | PASS |

第 7 条按契约要求传入两个独立参数（两条命令式 `unittest` 用例名），实测 `Ran 2 tests ... OK`，exit 0。审查者**未**把执行者报告中的 exit code 当作结论，而是逐条重跑。

## 三、独立核验明细（对应任务要求 A–J）

### A. 提交真实性

- `git log --oneline -5`：`c27b7c7`、`d238ba2`、`cdf55e9`、`a979d04`、`538d634`。两个目标提交存在、顺序正确，基线为 `cdf55e9`。
- `git show --stat d238ba2`：`108 files changed, 484 insertions(+), 1409 deletions(-)`，与执行者自述一致。
- `git show --stat c27b7c7`：`5 files changed, 59 insertions(+), 1 deletion(-)`，与自述一致。
- `git status --short`：工作区干净，仅有一个**未跟踪**的 `.pipeline/metrics/*.json`，由本轮测试运行自动生成（`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 未覆盖所有路径写入）。审查者未删除、未提交该文件。
- 冻结文件核查：两个提交均**未**触及 `docs/tasks/**`、`goal.md`、`IDEA.md`、`implement-plan.md`（`git show --stat --name-only` 过滤结果为空）。
- `.pipeline/metrics/` 删除数：**0**（`git diff --diff-filter=D -- .pipeline/metrics/` 为空）。

### B. 87 个删除

- `git diff cdf55e9 d238ba2 --name-status --diff-filter=D | wc -l` = **87**。
- 87 个被删文件中，命中 7 个保留名的数量为 **0**（反向 grep 计数 = 87，即全部为非保留名）。
- 父目录分布：`.pipeline/planning-run-lifecycle` 43、`.pipeline/pipeline-tools-v1` 23、`.pipeline/pipeline-tools-v1-continuation-1` 11、`.pipeline/implement-plan-coverage-repair-continuation-2` 4、`.pipeline/task-evidence-reconcile` 3、`.pipeline/planning-driven-vertical-pipeline` 3。
- 被删内容类型为原始日志（`*.log`、`*.raw.log`）、握手 JSON、探针脚本、旧 review 报告等过程产物，符合「非保留集」定义。

### C. 前向闸门（核心功能）

实跑对比：

| 命令 | 结果 | exit |
| --- | --- | --- |
| `python -m pipeline_tools scope history . --evidence-root .pipeline` | FAIL，列出 87 条 `d238ba2` 的删除违规 | **4** |
| `python -m pipeline_tools scope history . --evidence-root .pipeline --since d238ba2` | PASS | **0** |
| `python -m pipeline_tools scope history . --evidence-root .pipeline --since cdf55e9` | FAIL，仍列出 87 条 `d238ba2` 违规 | **4** |

**重要澄清**：任务委派说明中预期「`--since cdf55e9` 应 pass」，但该预期与契约语义不符。契约与 `references/acceptance-evidence.md` 明确定义 `--since <commit>` 扫描 `<commit>..HEAD`，且 `d238ba2` **就是执行清理的那次提交**；`cdf55e9` 是它的父提交，因此 `cdf55e9..HEAD` 必然包含清理提交自身的删除，报违规是正确行为，不是缺陷。用 `--since d238ba2`（清理提交之后）验证，退出码 0 PASS，证明前向闸门按设计工作。该点应记入需主代理注意的「委派预期与契约语义不符」，而非执行者缺陷。

代码核验：

- `pipeline_tools/core.py:226` `commit_history_check(..., since: str | None = None)`；`:235` `revision_range = f"{since}..HEAD" if since else "--all"`；省略 `since` 时行为与旧版完全一致。
- `pipeline_tools/core.py:26` `RETAINED_EVIDENCE_NAMES = REPORT_NAMES + MACHINE_RESULT_NAMES + ("finalization.json",)`；`:255` 内联 7 元素集合已改为引用该常量。
- `pipeline_tools/__main__.py:206` `history.add_argument("--since")`；`:1012` 透传 `since=args.since`。
- `pipeline_tools/planning.py:28` 导入常量；`:2148` `retained = list(RETAINED_EVIDENCE_NAMES)`，与 `commit_history_check` 共用同一常量（满足「单点定义」要求）。

### D. 契约文档

- `references/compat-and-migration.md` 中原句「已保存的证据文件（包括成功时的原始输出）可保留作为历史记录」**已删除**（grep 无命中），并在 diff 中替换为指向保留集与前向基线的表述。
- 7 个保留文件明文契约位置：
  - `references/acceptance-evidence.md:91`：「一个成功完成并已最终化的任务目录，只保留 7 个文件：`executor-report.md`、`review-report.md`、`final-check.md`、`executor-result.json`、`reviewer-result.json`、`final-result.json`、`finalization.json`。」
  - `references/metrics-contract.md:118`：同上并注明由 `RETAINED_EVIDENCE_NAMES` 单点定义。
  - `references/acceptance-evidence.md:97-101` 新增「前向基线闸门」节，明确 `--since` 语义与退出码。
- 裁决记录写在 `executor-report.md` 第四节（文本内容），**未**在 `.pipeline/` 下新建独立文件（`find .pipeline -name '*adjudicat*' -o -name '*裁决*'` 无命中），因此不构成自指违规。

### E. `scripts/validate_task_sheet.py` 的 schema 4 支持

- 文档字符串由 schema 3 扩展到 schema 3 and 4。
- `FORBIDDEN_SCHEMA3_HEADINGS` 更名为 `FORBIDDEN_PROCESS_RECORD_HEADINGS`。
- 新增 `REQUIRED_SCHEMA4_ACCEPTANCE_FIELDS = ("- 测试：", "- 命令：", "- 证据等级：")`。
- `if schema == 3` 改为 `if schema in (3, 4)`；验收字段按 schema 选择集合。
- 实跑：`python scripts/validate_task_sheet.py docs/tasks/evidence-retention-forward-gate.md` → `OK: valid task sheet`，exit **0**。此前该脚本对本任务单报 45 条假错误，现已消除。

### F. `forbidden_paths` 条件化

- `pipeline_tools/planning.py:1551 _task_forbidden_paths(task, plan)`：收集任务资源与所属 operation 资源，若任一规范化路径等于 `.pipeline` 或以 `.pipeline/` 开头（`touches_pipeline`），则**不**追加 `.pipeline/** existing history`，否则追加。
- `pipeline_tools/planning.py:1615 _task_sheet_text` 的 `forbidden_paths` 已由硬编码列表改为调用该函数。
- 实跑：本任务单契约 `forbidden_paths` = `["goal.md", "implement-plan.md", "IDEA.md"]`，不含 `.pipeline/** existing history`，与其触及 `.pipeline/` 的资源一致，消除自相矛盾。与 `op-decouple-generated-forbidden-paths` 意图一致。

### G. 测试 7 修复

- `tests/test_git_checks.py:167` 方法 `test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt` 在 `git init` 后（`:170-171`）补入 `git config user.email/user.name`，与同文件其余方法约定一致。
- 剥离全局 identity 实跑：`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null ... python -m unittest ...test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt` → `Ran 1 test ... OK`，exit **0**（修复前该模式下 `git commit` 退出 128 → exit 1）。

### H. 九条验收

见第二节表；全部 exit 0。

### I. 全量测试

`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests`

- `Ran 262 tests in 213.776s`
- `OK`
- exit **0**

与执行者报告「Ran 262 tests ... OK」一致。（执行者报告中另提到此前 261 的计数已自行更正为 262。）

### J. 执行者证据

- `executor-report.md`：六个 operation 均有执行记录；引用的证据仅 `executor-report.md` 自身与本轮运行的命令，**未**引用任何已删除的原始日志（符合 `goal.md:51`）。
- `executor-result.json`：JSON 合法；`identity.product_head` 与 `identity.head` 均 = `cdf55e9b9ec7b1322d66790e3d2fee244ffe22fa`（等于契约基线 `cdf55e9`，符合委派说明的预期值）；9 条 acceptance 状态均为 `pass`、`exit_code` 0；含 `unverified` 与 `resolved` 字段。

## 四、发现的问题（与执行者自述不符之处）

1. **委派说明中的 `--since cdf55e9` 预期错误（非执行者缺陷）**：委派要求「`--since cdf55e9` 应 pass」，但契约语义下 `cdf55e9..HEAD` 包含清理提交 `d238ba2`，必然报违规。实际用 `--since d238ba2` 验证得 exit 0 PASS。这是委派方对基线的选取错误，不是产品缺陷。已在本报告第二节/第三节 C 记录。
2. **执行者自述「文件数与 insertions/deletions」经核验准确**，未发现虚报。
3. 未发现验收测试被弱化、跳过或仅凭自述判定通过的情况；审查者逐条重跑复核。

## 五、对超范围删除的独立评估

**事实**：`op-delete-drifted-evidence.resources` 列出的 6 个目录为 `planning-run-lifecycle/`、`pipeline-tools-v1/`、`pipeline-tools-v1-continuation-1-repair-continuation-1/`、`implement-plan-coverage-repair-continuation-2/`、`planning-driven-vertical-pipeline/`、`task-evidence-reconcile/`。87 个删除中，11 个来自 `.pipeline/pipeline-tools-v1-continuation-1/`（**不在**上述 resource 列表内，也不在契约 `allowed_paths` 内）。

**独立核验**：

- 两个路径作为**带斜杠的目录前缀**互不覆盖：`.pipeline/pipeline-tools-v1-continuation-1/` 不是 `.pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/` 的前缀（`-repair-continuation-1` 段不同）。执行者的这一表述正确。
- 这 11 个文件为真实漂移产物（`capability-handshake.json`、`*.raw.log`、`final-review-report.md`、`re-review-report.md`、`runtime-preflight-pnpm10.json`、`pnpm10-version.log` 等），类型与其余 76 个一致。
- 契约 `resources` 指向的 `...-repair-continuation-1/` 目录内**确无**非保留文件可删（当前仅含 `executor-report.md`、`executor-result.json`）。

**评估**：这是本任务唯一的实质越界。执行者面临「按契约字面路径执行 → 需求目标（清空真实漂移集）落空」与「按真实漂移集执行 → 超出 `allowed_paths`」的冲突，选择了后者并在 `executor-report.md` 第四节显式留痕、不删除证据、不回滚。

审查者倾向认为该处置**可接受但需终审确认**：

- 删除对象是流程过程产物，非用户代码、非冻结文件、非 `.pipeline/metrics/`，可逆性风险低（内容仍在 `cdf55e9` 历史中）。
- 删除方向与需求目标一致，且留痕完整，未隐瞒。
- 但严格按机械范围规则，路径确实超出 `allowed_paths`，属越界行为，不应由执行者或审查者单方面默认豁免。

因此整任务判定为 **ACCEPT WITH CONDITIONS**，将此项上升为主代理终审裁决项。

## 六、未验证项

- 合并到 main 未执行（按非目标不应执行）。
- 主代理终审 `final-check.md` 未执行。
- 11 个超范围删除的最终裁决未做，留待主代理。
- `.pipeline/metrics/` 长期增长趋势（`assumption-metrics-untracked-count-grows`）未做跨任务验证。
- 执行者报告第七节所述「偶发失败触发瞬态无法归因」——审查者仅确认了确定性复现（剥离全局 identity 必失败、修复后必通过），未复现那次瞬态本身。