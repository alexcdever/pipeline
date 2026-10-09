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
{"schema": 2, "task_id": "post-merge-evidence-identity", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 3, "status": "PASS", "head": "d1b6376c9e3819fa0640b80de7d9983022ae069c", "sheet_revision": 4, "sheet_sha256": "c32e3c23c23cb830ff867374e1be927880700fc8cd21a88c0654eff1a7dc91a9", "observed_at_commit": "d1b6376c9e3819fa0640b80de7d9983022ae069c", "generated_at": "2026-10-09T00:57:52Z", "commands": [{"command": "python -m pytest -q tests/test_evidence.py -k post_merge_identity_uses_task_id_and_revision_only", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_rejects_revision_mismatch", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_rejects_task_id_mismatch", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_requires_main_worktree_reverification", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k pre_merge_commit_identity_is_not_weakened", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_identity_agrees_on_task_and_revision", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all contract acceptance commands for this task re-run by the main agent in the main worktree with exit code 0", "main worktree full suite passes: 395 passed, 28 subtests passed, exit code 0", "compileall exit code 0; git diff --check exit code 0", "the post-merge identity rule judges this evidence by task_id and sheet revision, which is why a merged delivery verifies without rewriting report identities"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker written in a following step", "the repo-wide pattern of unresolvable root-relative evidence_refs in older reports is recorded but not fixed here"]}
```
