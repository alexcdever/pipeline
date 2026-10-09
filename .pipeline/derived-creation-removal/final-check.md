# Final check

主代理最终检查，**合并后版本**。本文件在合并后于主工作树内重写并重跑，作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`b9aa5342496c6f0cd1bbfa3f6ba9c822a096a888`（`merge derived creation removal`），父提交 `f1e97e8`（main）与 `0253f58`（任务分支尖端）
- 主工作树根：`D:/Projects/Skills/pipeline`

## 交付意义

派生任务的创建路径已移除：`create_derived_dispatch` 与 `dispatch derived-create` 不再存在；新任务计划声明 `derived` 或派生形态一律 fail-closed 拒绝；生成器不再产出派生任务单。**历史读取完整保留**：`pipeline_tools/contract.py` 与契约基线逐字节相同，含 `derived_from` 的 7 张历史单全部仍通过 `task validate`，父类型的链路收紧与证据下限不变。文档改为"三类任务 + 新任务不再派生 + `dependencies` 表达接替 + 历史只读"，`SKILL.md` 升到 `0.17.0` 并新增 `v0.16.0 → v0.17.0` 兼容条目。

## 合并后本人在主工作树根重跑的内容

1. 五条契约验收测试：逐条退出码 0。
2. 全量测试：`388 passed, 30 subtests passed`，退出码 0。
3. 依赖可加载；`compileall` 与 `git diff --check` 退出码 0。
4. `contract.py` 与契约基线 diff 为 0 行。

## 未验证项与遗留（登记给 T3）

- 三条非阻塞审查发现：`README.md:29` 归因表述易误读；被删用例原覆盖的"保留父现场"断言随载体函数消失；`task-design.md` 的 `contract.py` 行号微偏。
- 报告 `head` 应记录"产生证据时的分支尖端"这一语义尚未写进 `references/`。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "derived-creation-removal", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 3, "status": "PASS", "head": "b9aa5342496c6f0cd1bbfa3f6ba9c822a096a888", "sheet_revision": 3, "sheet_sha256": "ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd", "observed_at_commit": "b9aa5342496c6f0cd1bbfa3f6ba9c822a096a888", "generated_at": "2026-10-09T04:59:35Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -c \"import pipeline_tools.core, pipeline_tools.planning, pipeline_tools.contract; print('imports ok')\"", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check f1e97e8..HEAD", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff cac7cfd HEAD -- pipeline_tools/contract.py", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref 0253f58 into main", "all five contract acceptance commands pass in the main worktree with exit code 0", "main worktree full suite passes: 388 passed, 30 subtests passed, exit code 0", "pipeline_tools modules import cleanly; compileall exit code 0; git diff --check exit code 0", "contract.py is still byte-identical to the contract baseline after the merge, so historical derived contracts stay readable", "the merge is a real merge commit with parents f1e97e8 and 0253f58"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker written in a following step", "three non-blocking review findings are recorded for later documentation work"]}
```
