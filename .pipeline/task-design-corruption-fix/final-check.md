# task-design-corruption-fix — 主代理最终检查

- task-id：`task-design-corruption-fix`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/task-design-corruption-fix`
- branch：`task-design-corruption-fix`
- role：main-final
- 冻结基线 HEAD：`f3b30a23a38be50b31ff387cc611c6b2c5877d97`
- 结论：**PASS**

## 身份与范围

- goal SHA-256 实测为 `9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`。
- 任务单校验 PASS，且 `git diff HEAD -- docs/` 为空，冻结任务单未改。
- 实现范围仅为 `references/task-design.md` 与 `tests/test_acceptance_id_and_template_compliance.py`，均在 allowed_paths；未改 `pipeline_tools/`、目标文件、其它任务单或历史证据。

## 独立验收

- `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_contains_no_replacement_character`：exit 0，1 test OK。
- `python -m unittest discover -s tests`：exit 0，318 tests OK（基线 317 + 1）。
- `python -m pipeline_tools --format json task validate docs/tasks/task-design-corruption-fix.md`：exit 0，status pass。

## 高风险断言

- 基线版本的 `references/task-design.md` 中恰有 3 个 U+FFFD，当前版本为 0。
- diff 仅把损坏的 `它���取` 修复为 `它读取`，周围文本没有变化。
- 新测试同时断言无 U+FFFD、存在 `_requires_full_chain` 与修复后的 `读取 derived_from.parent_task_type`，不是恒真测试。
- 历史 `.pipeline/` 证据中的 U+FFFD 未修改，符合本任务非目标。

## 证据

证据目录含 executor、reviewer、main-final 三份 Markdown 报告与三份 JSON 机器结果；无 `.log`/`.jsonl`。两份已有报告的 pipeline-evidence 块均为 schema 1、status PASS、assertions 为非空字符串数组。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "task-design-corruption-fix",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/task-design-corruption-fix",
  "branch": "task-design-corruption-fix",
  "role": "main-final",
  "round": 1,
  "status": "PASS",
  "commands": [
    {"command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_contains_no_replacement_character", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-design-corruption-fix", "evidence_ref": "final-check.md"},
    {"command": "python -m unittest discover -s tests", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-design-corruption-fix", "evidence_ref": "final-check.md"},
    {"command": "python -m pipeline_tools --format json task validate docs/tasks/task-design-corruption-fix.md", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-design-corruption-fix", "evidence_ref": "final-check.md"}
  ],
  "assertions": [
    "active task-design.md 的 U+FFFD 从 3 修复到 0",
    "diff 仅包含它读取的预期修复与一个回归测试",
    "全量 318 tests OK，基线 317 之上新增 1",
    "历史证据未修改且实现范围合规"
  ],
  "evidence_refs": ["final-check.md", "executor-report.md", "review-report.md"],
  "unverified": [
    "历史证据中的 U+FFFD 未清理，按本任务非目标保留"
  ],
  "recommendation": "ready_to_merge"
}
```