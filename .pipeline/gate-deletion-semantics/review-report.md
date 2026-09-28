# 审查报告：gate-deletion-semantics

```json
{
  "task_id": "gate-deletion-semantics",
  "role": "reviewer",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics",
  "branch": "gate-deletion-semantics",
  "round": 1,
  "generated_at": "2026-09-28T03:40:00Z",
  "baseline_head": "692ee6387ea2e60d53d63680235906096ed90903",
  "product_head": "692ee6387ea2e60d53d63680235906096ed90903",
  "reviewed_commit": "12e302cad2a4c6670c4490aa4a4bbde07d3c9440",
  "test_count": 268,
  "commands": [
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline --since cdf55e9", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline --since 8f1f1e0", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline", "exit_code": 4, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline --since 692ee63", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_delete_retained_evidence_is_a_violation", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_add_non_retained_evidence_still_violates", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics"}
  ]
}
```

## 结论摘要

`commit_history_check` 的删除方向修复**语义正确、边界完整、未越界**。四条新测试均有实质断言，覆盖了「删除保留文件仍违规」的反向情形。默认全量扫描仍 exit 4，证明闸门未被整体放宽。5 条 acceptance 全部实跑通过；全量 268 条测试通过。

**判定：ACCEPT WITH CONDITIONS** —— 代码与测试可接受；两项条件见文末，均为记录/文档一致性，不阻塞合并。

---

## A. 提交真实性

| 检查 | 命令 | 结果 |
|---|---|---|
| 提交顺序 | `git log --oneline -6` | `12e302c` → `692ee63` → `4a2336c` → `8f1f1e0` … 顺序正确 |
| 提交统计 | `git show --stat 12e302c` | **8 files changed, 297 insertions(+), 7 deletions(-)** —— 与执行者自述完全一致 |
| 基线未变 | `git rev-parse 692ee63` | `692ee6387ea2e60d53d63680235906096ed90903` —— 未变 |
| main 未动 | `git -C <主仓库> rev-parse main` | `692ee6387ea2e60d53d63680235906096ed90903` —— 未变 |
| HEAD | `git rev-parse HEAD` | `12e302cad2a4c6670c4490aa4a4bbde07d3c9440` |
| 工作区 | `git status --short` | 空（干净） |
| stash | `git stash list` | 空 —— 无残留 |
| worktree | `git worktree list --porcelain` | 仅主树(main=692ee63) 与本任务树(branch=gate-deletion-semantics, HEAD=12e302c)，符合契约 |

### amend 是否越界 —— 核验通过

`git reflog -20` 原文：

```
12e302c HEAD@{0}: commit (amend): fix(core): distinguish deletion from addition in evidence history check
97c953b HEAD@{1}: commit: fix(core): distinguish deletion from addition in evidence history check
692ee63 HEAD@{2}: reset: moving to HEAD
692ee63 HEAD@{3}:
```

- `git rev-parse 97c953b` → `97c953b6fc796d53a195553ac490d02e0203fc4b`（仍可达）
- `git fsck --lost-found` 同时列出 `dangling commit 97c953b...` —— 旧提交作为悬挂对象保留，未被回收。
- amend **只重写了它自己刚生成的提交** `97c953b`（`HEAD@{1}`），父提交仍是 `692ee63`（`HEAD@{2}` 为 reset 到 692ee63）。
- **结论**：amend 仅影响执行者自己的提交，未触碰冻结基线 `692ee63`，主仓库 `main` 仍指向 `692ee63`。未越界。

### 冻结文件与 metrics

- `git log --oneline --name-only 692ee63..HEAD -- docs/tasks goal.md IDEA.md implement-plan.md` → **无输出**，未触碰任何冻结文件。
- `git log --diff-filter=D ... -- .pipeline/metrics` → **无输出**，未删除 `.pipeline/metrics/` 下任何文件。
- 本提交向 `.pipeline/metrics/` 新增 2 个指标事件（`A`），是工具自动写入的生命周期事件，非删除。

---

## B. 判定逻辑

### 改动后的判定代码（`pipeline_tools/core.py:245-262`，原文）

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

### `retained == deleting` 真值表

| 方向 | `deleting` | `retained` | `retained == deleting` | 是否违规 | 契约要求 | 一致？ |
|---|---|---|---|---|---|---|
| `A` 新增 + 非保留 | False | False | True | **违规** | 违规 | ✅ |
| `A`/`M` 新增/修改 + 保留 | False | True | False | 放行 | 放行 | ✅ |
| `D` 删除 + 非保留 | True | False | False | **放行** | 放行 | ✅ |
| `D` 删除 + 保留 | True | True | True | **违规** | 违规 | ✅ |

四个象限全部与契约一致。等价写法：非删除且非保留 → 违规；删除且保留 → 违规。

### 未改动的分支

- 进度日志分支仍在方向判定**之前**无条件命中，未改动（`is_progress_log_path` 函数体 `core.py:462-471` 未变）。
- `.pipeline/metrics/` 豁免分支（`in_metrics` 短路）未改动。
- `revision_range = f"{since}..HEAD" if since else "--all"` 未改动，`--since` 前向基线语义未变。
- `RETAINED_EVIDENCE_NAMES`（`core.py:26`）成员未增删。

### `R*` 重命名语义

`'R100'.startswith('D')` → **False**。即重命名被当作非删除处理，走「非保留即违规」原路径。契约只规定 `A`/`M`/`D`，`R*` 属**未规定情形**；沿用旧行为（重命名非保留名 = 违规）是保守选择，不会放宽闸门。**可接受**。

---

## C. 前向闸门行为（实跑）

| # | 命令 | 退出码 | 关键输出 |
|---|---|---|---|
| C1 | `scope history . --evidence-root .pipeline --since cdf55e9` | **0** | `PASS` |
| C2 | `scope history . --evidence-root .pipeline --since 8f1f1e0` | **0** | `PASS` |
| C3 | `scope history . --evidence-root .pipeline`（默认全量） | **4** | `FAIL:` 大量 `A`/`R`/进度日志类历史违规，**不含任何 `D` 非保留删除** |
| C4 | `scope history . --evidence-root .pipeline --since 692ee63` | **0** | `PASS` |

**关键**：C3 默认全量仍 exit 4 —— 证明闸门**未被整体放宽**，只收紧了删除方向。C3 输出中的违规全部是 `A`（新增非保留）、`R065`/`R090`/`R100`（重命名非保留，仍按非删除判违规）与 `-progress.jsonl`（进度日志），**没有一条是 `D` 非保留删除**，与修复目标一致。

与执行者自述核对：**完全一致**（前两条 0、第三条 4、第四条 0）。

stash 检查：`git stash list` 为空，**无残留**。

---

## D. 迁移的既有测试

`tests/test_git_checks.py:147` `test_commit_history_check_evidence_path_guard`（改后完整断言）：

```python
    def test_commit_history_check_evidence_path_guard(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); subprocess.run(['git', 'init', '-q'], cwd=p, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=p, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=p, check=True)
            (p / 'src').mkdir(); (p / 'src' / 'app.py').write_text('x')
            subprocess.run(['git', 'add', '.'], cwd=p, check=True); subprocess.run(['git', 'commit', '-qm', 'base'], cwd=p, check=True)
            evidence = p / '.pipeline' / 'demo'; evidence.mkdir(parents=True)
            (evidence / 'raw.log').write_text('raw')
            subprocess.run(['git', 'add', '.'], cwd=p, check=True); subprocess.run(['git', 'commit', '-qm', 'bad evidence'], cwd=p, check=True)
            (evidence / 'raw.log').unlink(); subprocess.run(['git', 'add', '-A'], cwd=p, check=True); subprocess.run(['git', 'commit', '-qm', 'delete evidence'], cwd=p, check=True)
            metrics = p / '.pipeline' / 'metrics'; metrics.mkdir(parents=True); (metrics / 'event.json').write_text('{}')
            subprocess.run(['git', 'add', '.'], cwd=p, check=True); subprocess.run(['git', 'commit', '-qm', 'metrics'], cwd=p, check=True)
            violations = commit_history_check(p, '.pipeline/demo')
            self.assertEqual(len(violations), 1, violations)
            self.assertIn('raw.log', violations[0])
            self.assertIn(' A ', violations[0])
```

- 构造序列：`base` → 新增 `raw.log`（`A`）→ 删除 `raw.log`（`D`）→ 新增 metrics（豁免）。
- 断言 `len(violations) == 1` 且该条含 ` A `（即来自新增，而非删除）。新语义下删除不再违规，故 2→1，且额外断言方向为 `A`。
- **实跑 F4**：`Ran 1 test ... OK`，exit 0。**核验通过**。

---

## E. 四条新测试

| 测试 | 关键断言 | 实质断言？ |
|---|---|---|
| `test_delete_non_retained_evidence_is_not_a_violation` | 提交 scratch.log 后记 `baseline`，再提交删除；`commit_history_check(..., since=baseline) == []` | ✅ 真实 `git init`+提交，基线取删除前实际 HEAD |
| `test_delete_retained_evidence_is_a_violation` | 提交 `executor-report.md` 后删除；`len(violations) == 1`，含 `executor-report.md` 与 ` D ` | ✅ **反向情形** |
| `test_add_non_retained_evidence_still_violates` | 全量仅新增 raw.log；`len == 1`，含 `raw.log` 与 ` A ` | ✅ 回归保护 |
| `test_references_acceptance_evidence_documents_deletion_semantics` | 读 `references/acceptance-evidence.md`，断言含 `commit_history_check`/`保留集`/`` `A` ``/`` `D` ``，且存在同时含 `` `D` ``+`保留集`+`删除` 的行 | ✅ 定向文档断言 |

**防修复过宽**：`test_delete_retained_evidence_is_a_violation` **正是**「删除保留文件仍违规」的反向情形，且断言消息含 ` D `，确认违规来自删除方向。修复**未过宽**。

全部 5 条实跑（F1–F5）均 `Ran 1 test ... OK`，exit 0。

---

## F. 5 条 acceptance 独立验证

全部命令在 worktree 根目录、`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 下实跑。

| # | acceptance-test ID | 测试 | 退出码 | 结果 |
|---|---|---|---|---|
| 1 | `acceptance-test-delete-non-retained-evidence-not-a-violation` | `GitChecks.test_delete_non_retained_evidence_is_not_a_violation` | 0 | PASS |
| 2 | `acceptance-test-delete-retained-evidence-is-a-violation` | `GitChecks.test_delete_retained_evidence_is_a_violation` | 0 | PASS |
| 3 | `acceptance-test-add-non-retained-evidence-still-violates` | `GitChecks.test_add_non_retained_evidence_still_violates` | 0 | PASS |
| 4 | `acceptance-test-forward-gate-guard-migrated` | `GitChecks.test_commit_history_check_evidence_path_guard` | 0 | PASS |
| 5 | `acceptance-test-retention-gate-docs-aligned` | `AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics` | 0 | PASS |

**5/5 PASS**，均为审查者独立实跑所得。

---

## G. 全量测试

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests
```

**Ran 268 tests in 212.499s — OK**，exit 0。与执行者自述 268 一致。基线 264 + 4 = 268，计数自洽。

---

## H. 执行者证据

- `executor-report.md`：三个 operation 均有记录（op-fix-deletion-status-branch / op-cover-deletion-semantics-with-tests / op-align-retention-gate-docs）。报告**未引用任何已删除的原始日志**——所有引用指向 `executor-report.md` 自身小节或当前存在的文件，符合 `goal.md:51`。
- `executor-result.json`：JSON 合法。5 条 acceptance 均 `pass`/`exit_code 0`。
- **不符之处**：`identity.head` 为 `692ee6387ea2...`（基线），`identity.commit` 为 `97c953b...`（amend 前的旧提交），**均非最终提交 `12e302c`**。该机器结果在 amend 之前生成，amend 后未重新生成身份。详见「与执行者自述不符之处」。

---

## 两个未决点独立评估

### 未决点 1：`references/metrics-contract.md:118` 未表述删除方向

该行原文：「`commit_history_check` 只承认 7 个保留文件名：…」。**无删除方向表述**。

- **是否在 allowed_paths 内**：是。任务单 `allowed_paths` 含 `references/**`，该文件在 `references/` 下，属允许范围。
- **是否本任务应有交付**：任务单三个 operation 中 `op-align-retention-gate-docs` 的资源是 `references/**`，且需求含 `requirement-retention-gate-docs-aligned`。执行者只改了 `references/acceptance-evidence.md`，未改 `metrics-contract.md`。acceptance-test-5 的 `test_ref` 仅指向 `acceptance-evidence.md`，故**契约的机械验收并未要求** `metrics-contract.md`。
- **评估**：这是文档一致性的**遗留缺口**，但不构成本任务验收失败——契约未把它列为 acceptance 断言。建议另开一条文档对齐任务，或在后续任务中一并修正。**不阻塞**。

### 未决点 2：`R*` 重命名语义未定义

- 契约只规定 `A`/`M`/`D`；`R*` 属**未规定情形**。
- `'R100'.startswith('D')` → False，即重命名按非删除处理（非保留名仍违规）。
- **评估**：沿用旧行为是保守、不放宽闸门的选择，且在 C3 默认全量中可见 `R065`/`R090`/`R100` 仍被判违规，行为符合「不整体放宽」。**可接受**。

---

## 发现的问题

1. **[条件] `executor-result.json` 身份陈旧**：`identity.head`/`identity.commit` 指向 amend 前的 `692ee63`/`97c953b`，非最终 `12e302c`。机器结果身份与最终提交不一致，建议主代理在终审时裁定是否要求重新生成该文件。
2. **[记录] `references/metrics-contract.md:118` 未同步删除方向表述**（见未决点 1），属文档一致性遗留，不阻塞。
3. **[说明] 本提交向 `.pipeline/metrics/` 新增 2 个指标事件**：这是工具自动写入的生命周期事件（`.pipeline/metrics/` 独立豁免），非违规。

---

## 未验证项

- 主代理终审（final-check）未做。
- 合并到 main、post-merge gate 未做。
- `executor-result.json` 的 amend 后新鲜度未由执行者重新生成（审查者不修改执行者产物）。

---

## 结论

**ACCEPT WITH CONDITIONS**

- 代码修复语义正确，四象限真值表与契约完全一致。
- 四条新测试均有实质断言，含反向情形，修复未过宽。
- 5 条 acceptance 独立实跑 5/5 PASS；全量 268 条 OK。
- 未触碰冻结文件、未删 metrics、amend 未越界、stash 无残留。
- 条件：`executor-result.json` 身份陈旧（建议终审裁定）；`metrics-contract.md:118` 文档方向表述缺失（建议另开任务）。