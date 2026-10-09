# Final check

主代理最终检查（第三层验证），round 2。

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1 | **BLOCKED**（决策点 4：安全回归文件在范围外） | 证据 `65c5772` |
| 范围修订 rev 1→2（补该文件、授权两处测试改写） | — | `cac7cfd` |
| 执行 round 2 | PASS | `b4ca117` / `4251e0e` |
| 独立审查 round 1 | **PASS** | `40df5ca` |
| 主代理最终检查 → **pre-merge 闸门抓到 `test_ref` 类名笔误** | FAIL | `1b384d2` |
| 范围修订 rev 2→3（修正 `CliTests`→`CLITests`） | — | `f1e97e8` |
| 执行 round 3 → round 4（修正 `head` 语义） | PASS | `875f4a5` / `d89ba7f` |
| 独立审查 round 2 | **PASS** | `198ad3a` |
| 主代理最终检查（本轮） | PASS | 本文件 |

## 两次卡片各自暴露的问题

1. **`test_ref` 类名笔误（我的错）**：`tests/test_cli.py` 定义的是 `CLITests`，我在契约里写成 `CliTests`。`pytest -k` 匹配不管类名，所以执行者与审查者两次都跑绿；只有 `gate pre-merge` 的"`test_ref` 方法必须真实存在于该类该文件"校验抓住了它。修订后由审查者走 pipeline 自己的校验路径确认五条 `test_ref` 全部可解析。
2. **`head` 语义**：报告 `head` 原先记"实现提交"，但契约被修订过（改的是 `docs/tasks/...`，不在 `.pipeline/` 下），于是 `b4ca117..HEAD` 含非证据改动 → 报告恒判过期。正确语义是**记录产生证据时的分支尖端**（它评判的状态就是当时的尖端）。执行与审查各自按此重出后，两条 head 错误依次消失。

## 本轮主代理亲自做的事

1. **重跑五条验收**（revision 3 下）：逐条退出码 0。
2. **重跑全量测试**：`388 passed, 30 subtests passed`，退出码 0。
3. **实现未变核对**：`b4ca117..HEAD` 中唯一非证据路径是任务单自身（两次修订）。
4. **`contract.py` 零 diff**；此前已独立只读复验 7 张含 `derived_from` 的历史单全部 `task validate` PASS。

## 未验证项与遗留（不阻塞）

- 合并后主工作树复验未进行。
- 三条非阻塞审查发现：`README.md:29` 的归因表述易误读；被删用例原覆盖的"失败时保留父现场"随载体函数消失；`task-design.md` 引用的 `contract.py` 行号微偏（改动前即如此）。
- **待并入 T3 的文档要点**：报告 `head` 应记录"产生证据时的分支尖端"这一语义，目前只存在于本轮实践里，未写进 `references/`。

## 结论

三层验证全部通过，范围与历史完好。**READY-TO-MERGE。**

```pipeline-evidence
{"schema": 2, "task_id": "derived-creation-removal", "worktree": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "branch": "derived-creation-removal", "role": "main-final", "round": 2, "status": "PASS", "head": "198ad3ada399b468fed1341e7ad4dd47cd3710e8", "sheet_revision": 3, "sheet_sha256": "ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd", "observed_at_commit": "198ad3ada399b468fed1341e7ad4dd47cd3710e8", "generated_at": "2026-10-09T04:52:59Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff cac7cfd HEAD -- pipeline_tools/contract.py", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check cac7cfd..b4ca117", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all five contract acceptance commands re-run by the main agent at contract revision 3 with exit code 0", "main agent full suite re-run: 388 passed, 30 subtests passed, exit code 0", "the only non-evidence change between the implementation commit and this head is the task sheet itself, from the two recorded amendments", "contract.py is byte-identical to the contract baseline: zero diff lines, so historical derived validation and the parent-type chain and evidence-floor rules are untouched", "this head records the branch tip at production, not the implementation commit, so later evidence commits count as evidence-only advancement"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["post-merge main-worktree re-verification pending", "three non-blocking review findings are recorded"]}
```
