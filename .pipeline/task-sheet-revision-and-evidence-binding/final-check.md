# Final check

主代理最终检查，**合并后版本**（重生成）。本文件在合并后于主工作树内重写并重跑，作为独立的 post-merge 证据提交。

## 为什么重生成

本任务此前因闸门/最终化链路自身的缺陷而被扣住（先是没有 `observed_at_commit`、状态为 BLOCKED，后来是 `evidence-finalize` 对 schema 2 报告一律判 invalid、以及最终化标记的 head 判据循环不可满足）。这些缺陷已由后续任务修复，现于当前合并头重做合并后复验并刷新本文件与 `final-result.json`。

## 本次在主工作树根重跑的内容

1. 本契约的全部验收命令：逐条退出码 0。
2. 全量测试：`395 passed, 28 subtests passed`，退出码 0。
3. `compileall` 与 `git diff --check` 退出码 0。

## 未验证项

- 本文件提交后才会写入最终化标记，随后执行 `evidence verify --phase finalized`。
- 仓库级已记录问题：较早报告里有不可解析的根相对 `evidence_refs`（不阻塞最终化，会给 `--phase finalized` 带噪声）；历史报告不重写。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "task-sheet-revision-and-evidence-binding", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 4, "status": "PASS", "head": "d1b6376c9e3819fa0640b80de7d9983022ae069c", "sheet_revision": 1, "sheet_sha256": "a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783", "observed_at_commit": "d1b6376c9e3819fa0640b80de7d9983022ae069c", "generated_at": "2026-10-09T00:57:52Z", "commands": [{"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all contract acceptance commands for this task re-run by the main agent in the main worktree with exit code 0", "main worktree full suite passes: 395 passed, 28 subtests passed, exit code 0", "compileall exit code 0; git diff --check exit code 0", "the post-merge identity rule judges this evidence by task_id and sheet revision, which is why a merged delivery verifies without rewriting report identities"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker written in a following step", "the repo-wide pattern of unresolvable root-relative evidence_refs in older reports is recorded but not fixed here"]}
```
