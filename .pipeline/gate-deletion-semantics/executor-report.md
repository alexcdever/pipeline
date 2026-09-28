# 执行者报告：gate-deletion-semantics

```json
{
  "task_id": "gate-deletion-semantics",
  "role": "executor",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics",
  "branch": "gate-deletion-semantics",
  "round": 1,
  "generated_at": "2026-09-28T03:09:17Z",
  "baseline_head": "692ee6387ea2e60d53d63680235906096ed90903",
  "product_head": "692ee6387ea2e60d53d63680235906096ed90903",
  "test_count": 268,
  "commands": [
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks tests.test_acceptance_id_and_template_compliance", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline --since cdf55e9", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"}
  ]
}
```

## 一、改动概览

缺陷：`commit_history_check` 取出 Git `--name-status` 的状态列（`A`/`M`/`D`/`R*`）后只把它当消息前缀打印，判定完全不使用方向维度，因此「删除非保留证据文件」这一契约要求的清理动作被与「新增违规文件」等同判为漂移。

期望语义：`D` 状态仅当被删文件 basename 属于 `RETAINED_EVIDENCE_NAMES` 时报违规；`A`/`M` 状态保持原判定（basename 不在保留集内则违规）。

## 二、三个 operation 的实际改动

### op-fix-deletion-status-branch（pipeline_tools/core.py）

- `pipeline_tools/core.py:221-235`：`commit_history_check` docstring 补充方向性语义说明（新增/修改按 basename 判，删除只在删保留文件时判违规）；`since` 前向基线语义未改动。
- `pipeline_tools/core.py:245-262`（判定主循环）：

改前（`:248-256`）：

```python
        status, paths = parts[0], parts[1:]
        for path in paths:
            normalized = _normalize_path(path)
            in_evidence = normalized == evidence_root or normalized.startswith(evidence_root.rstrip("/") + "/")
            in_metrics = normalized == metrics_root or normalized.startswith(metrics_root.rstrip("/") + "/")
            if is_progress_log_path(normalized):
                violations.append(f"{current_commit}: {status} {normalized} (progress log must not enter Git)")
            elif in_evidence and not in_metrics and Path(normalized).name not in RETAINED_EVIDENCE_NAMES:
                violations.append(f"{current_commit}: {status} {normalized}")
    return violations
```

改后：

```python
        status, paths = parts[0], parts[1:]
        deleting = status.startswith("D")
        for path in paths:
            normalized = _normalize_path(path)
            in_evidence = normalized == evidence_root or normalized.startswith(evidence_root.rstrip("/") + "/")
            in_metrics = normalized == metrics_root or normalized.startswith(metrics_root.rstrip("/") + "/")
            if is_progress_log_path(normalized):
                violations.append(f"{current_commit}: {status} {normalized} (progress log must not enter Git)")
            elif in_evidence and not in_metrics:
                # Removing a retained file is drift; removing scratch evidence is
                # the cleanup the retention contract asks for.
                retained = Path(normalized).name in RETAINED_EVIDENCE_NAMES
                if retained == deleting:
                    violations.append(f"{current_commit}: {status} {normalized}")
    return violations
```

关键点：

- `deleting = status.startswith("D")` 覆盖 `D` 与 `R*` 之外的纯删除码；`A`/`M`/`R*` 均为 `False`，走原「非保留即违规」路径。
- `retained == deleting` 等价于两条规则：非删除（`deleting=False`）且非保留（`retained=False`）→ 违规；删除（`True`）且保留（`True`）→ 违规。删除非保留（`True==False`）和新增保留（`False==True`）都不违规——前者是本次修复目标，后者本就合规。
- 进度日志分支未改动，仍在方向判定之前无条件命中 `progress log must not enter Git`。
- `RETAINED_EVIDENCE_NAMES`（`core.py:26`）成员未增删；`.pipeline/metrics/` 豁免分支未改动；`--since` 前向基线语义未改动。

### op-cover-deletion-semantics-with-tests（tests/）

- `tests/test_git_checks.py`：新增 3 条方向性测试（见第三节），迁移既有守卫测试断言（见第四节）。
- `tests/test_acceptance_id_and_template_compliance.py`：新增 `test_references_acceptance_evidence_documents_deletion_semantics`。

### op-align-retention-gate-docs（references/acceptance-evidence.md）

- `references/acceptance-evidence.md:95`：把「文件名不在保留集内即报违规」改为按方向表述——新增/修改不在保留集内违规；删除只在被删文件属于保留集时违规；进度日志无论方向都单独报；metrics 豁免不变。

## 三、验收测试运行记录

全部在 worktree 根目录运行，环境变量 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

| # | 验收测试 ID | 测试 | 命令 | 结果 |
|---|---|---|---|---|
| 1 | acceptance-test-delete-non-retained-evidence-not-a-violation | `tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation` | `python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation` | `Ran 1 test ... OK`，exit 0 |
| 2 | acceptance-test-delete-retained-evidence-is-a-violation | `tests.test_git_checks.GitChecks.test_delete_retained_evidence_is_a_violation` | `python -m unittest tests.test_git_checks.GitChecks.test_delete_retained_evidence_is_a_violation` | `Ran 1 test ... OK`，exit 0 |
| 3 | acceptance-test-add-non-retained-evidence-still-violates | `tests.test_git_checks.GitChecks.test_add_non_retained_evidence_still_violates` | `python -m unittest tests.test_git_checks.GitChecks.test_add_non_retained_evidence_still_violates` | `Ran 1 test ... OK`，exit 0 |
| 4 | acceptance-test-forward-gate-guard-migrated | `tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard` | `python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard` | `Ran 1 test ... OK`，exit 0 |
| 5 | acceptance-test-retention-gate-docs-aligned | `tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics` | `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics` | `Ran 1 test ... OK`，exit 0 |

针对性套件（两文件合并）：`Ran 36 tests in 17.912s ... OK`，exit 0。

全量门禁：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests` → `Ran 268 tests in 212.702s ... OK`，exit 0。基线 264（主工作树合并后），本次新增 4 条，计数一致。

未受影响的既有测试（已核实只新增、无删除，无需迁移）：`test_commit_history_check_keeps_exactly_the_documented_retained_names`、`test_scope_history_since_baseline_ignores_earlier_violations`；两条均在全量套件中通过。

## 四、迁移的既有测试

`tests/test_git_checks.py:147` `test_commit_history_check_evidence_path_guard` 构造「新增 raw.log」+「删除 raw.log」两个提交。

改前断言：

```python
            violations = commit_history_check(p, '.pipeline/demo')
            self.assertEqual(len(violations), 2)
            self.assertTrue(all('demo' in value for value in violations))
```

改后断言：

```python
            violations = commit_history_check(p, '.pipeline/demo')
            self.assertEqual(len(violations), 1, violations)
            self.assertIn('raw.log', violations[0])
            self.assertIn(' A ', violations[0])
```

新语义下删除不再违规，故违规数由 2 变 1；额外断言该条违规来自 `A` 方向，而非删除。该迁移与判定改动在同一次提交内完成，无中间态红。

## 五、新增测试

| 文件 | 类 | 方法 | 断言内容 |
|---|---|---|---|
| `tests/test_git_checks.py` | `GitChecks` | `test_delete_non_retained_evidence_is_not_a_violation` | 先提交 scratch.log（记 baseline），再提交删除；`commit_history_check(..., since=baseline)` 必须返回 `[]` |
| `tests/test_git_checks.py` | `GitChecks` | `test_delete_retained_evidence_is_a_violation` | 提交 `executor-report.md` 后删除；违规数 `== 1`，消息含 `executor-report.md` 与 ` D ` |
| `tests/test_git_checks.py` | `GitChecks` | `test_add_non_retained_evidence_still_violates` | 全量扫描仅新增 raw.log；违规数 `== 1`，消息含 `raw.log` 与 ` A `（回归保护） |
| `tests/test_acceptance_id_and_template_compliance.py` | `AcceptanceIdAndTemplateComplianceTests` | `test_references_acceptance_evidence_documents_deletion_semantics` | `references/acceptance-evidence.md` 含 `commit_history_check`、`保留集`、反引号 `` `A` ``/`` `D` ``，且存在同时含 `` `D` ``、`保留集`、`删除` 的行 |

三条 git 测试均使用真实 `git init` + 提交的临时仓库，`since=` 基线取删除前的实际 HEAD，非空断言。

## 六、前向闸门行为验证

修复前后对照，同一 worktree、同一基线 `cdf55e9`（evidence-retention-forward-gate 任务单冻结提交）：

| 命令 | 修复前 | 修复后 |
|---|---|---|
| `python -m pipeline_tools scope history . --evidence-root .pipeline --since cdf55e9` | exit **4**（`FAIL:`，87 条 `D .pipeline`） | exit **0**（`PASS`） |
| `python -m pipeline_tools scope history . --evidence-root .pipeline --since 8f1f1e0` | — | exit **0**（`PASS`），`: D ` 计数 0 |
| `python -m pipeline_tools scope history . --evidence-root .pipeline`（默认全量） | exit 4 | exit 4，仍报 `A`/`R`/进度日志类历史违规（如 `c5c554f9...: A .pipeline/.../acceptance-1-2.txt`），**不含任何 `d238ba2` 的 87 条 `D`** |

修复前数据由 `git stash push -- pipeline_tools/core.py` 后重跑同一命令取得，随后 `git stash pop` 恢复；stash 已成功回滚并 pop，工作区改动完整。

对照结论：基线 `cdf55e9` 之前/之后的历史不变，删除非保留证据不再判违规；默认全量扫描仍对新增/重命名类历史漂移报 `DRIFT`（exit 4），说明闸门未被整体放宽，只收紧了删除方向。

## 七、未验证项

- 独立审查（reviewer）未做。
- 主代理终审（final-check）未做。
- 合并到 main 未做。
- 未重写 Git 历史、未 push、未删除 worktree。
- 未运行 post-merge gate。

## 八、困难与解决

1. **删除方向与保留集的关系容易写反**。初始设想是「删除时若不在保留集则跳过」，实测发现需同时保证「新增保留文件」不误报；最终用 `retained == deleting` 单一表达式统一四个象限，逻辑等价且可读。
2. **迁移与实现必须同提交**。先改判定再改测试会造成中间态红；本次在同一提交内完成，并额外断言 ` A ` 方向以区分新旧行为。
3. **`--since` 基线不得改动**。`revision_range` 与 `since` 参数完全未触碰，仅改内层方向判定。