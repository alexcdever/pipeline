# Final check

主代理最终检查（第三层验证）。

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1（rev 2 旧设计） | PASS | `8b1ba98` / `aeefd29` |
| **设计变更**：改用阶段分工（rev 3） | — | `360ec91` |
| 执行 round 2 | PASS | `f39d1f9` / `34c7fa5` |
| **范围补充**：CLI 入口入范围（rev 4） | — | `fe999dc` |
| 执行 round 3 | PASS | `270ebc0` / `b89f764` |
| 独立审查 round 1 | **PASS** | `0d29bb6` |
| 主代理最终检查（本轮） | PASS | 本文件 |

契约经两次修订（revision 2→3→4），每次都由 `task amend` 登记裁决与结构化差异；执行者的旧证据按"验证面变更即作废"的规则重做过两轮。

## 本轮主代理亲自做的事

1. **身份核对**：任务分支 `330314c → … → b89c5b1 → f39d1f9 → 34c7fa5 → … → 270ebc0 → b89f764 → 0d29bb6`；主工作树未被触碰。
2. **重跑七条验收**：逐条独立执行，退出码全部 0。
3. **重跑全量测试**：`387 passed, 28 subtests passed`，退出码 0（基线 367）。
4. **范围核对**：`fe999dc..270ebc0` 共 9 个路径，全部落在 revision 4 的 `allowed_paths` 内；`forbidden_paths` 零改动。
5. **死代码核对**：`merged_task_branch_identity` 在产品代码中引用数为 0。
6. **编译 / 空白**：`compileall` 0；`git diff --check` 0。

## 独立审查的结论与遗留发现

审查结论 PASS，并用自建夹具独立复现了阶段分工，其中包含把改动前的代码抽出后对 active 阶段错误列表做**逐字节比对**（未合并分支 / 非祖先 head / 非规范 worktree / 分支不存在四种情形完全一致）。

三条**非阻塞**发现，登记为后续处理，不在本任务范围内解决：

1. `references/merge-and-recovery.md` 的"合并后"小节末尾仍有一句旧话，与新写的阶段分工段落矛盾（文档一致性缺陷）。
2. `reconcile.py:151` 仍以默认 `active` 阶段调用 `evidence_verify`，因此混合身份不再报冲突、但仍会累积身份错误，合并后的交付在 `reconcile` 下仍达不到 PASS。
3. 契约把 `observed_at_commit` 列为 finalized 阶段必需字段，历史形态证据在 post-merge 下每个报告因此多两条错误。

## 未验证项

- 合并后主工作树复验未进行——post-merge 阶段硬要求，合并后会重跑并更新本文件与 `final-result.json`，并提交 `finalization.json`。

## 结论

三层验证全部通过，范围与历史完好。**READY-TO-MERGE。**

```pipeline-evidence
{"schema": 2, "task_id": "post-merge-evidence-identity", "worktree": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "branch": "post-merge-evidence-identity", "role": "main-final", "round": 1, "status": "PASS", "head": "270ebc0192bbd7273b1c207eec26872bc744bbc8", "sheet_revision": 4, "sheet_sha256": "c32e3c23c23cb830ff867374e1be927880700fc8cd21a88c0654eff1a7dc91a9", "observed_at_commit": "270ebc0192bbd7273b1c207eec26872bc744bbc8", "generated_at": "2026-10-08T19:11:08Z", "commands": [{"command": "python -m pytest -q tests/test_evidence.py -k post_merge_identity_uses_task_id_and_revision_only", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_rejects_revision_mismatch", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_rejects_task_id_mismatch", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_requires_main_worktree_reverification", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k pre_merge_commit_identity_is_not_weakened", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_identity_agrees_on_task_and_revision", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check fe999dc..270ebc0", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --name-only fe999dc 270ebc0", "cwd": "D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all seven contract acceptance commands re-run by the main agent at implementation head 270ebc0 with exit code 0", "main agent full suite re-run: 387 passed, 28 subtests passed, exit code 0", "nine changed paths between the contract baseline and the implementation all fall inside the revision 4 allowed_paths; zero forbidden-path changes", "merged_task_branch_identity has zero references left in product code", "compileall exit code 0 and git diff --check exit code 0 over the implementation range", "the independent review (0d29bb6) reproduced the phase split with its own fixtures, including a byte-identical error-list comparison of the active phase before and after the change"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["post-merge main-worktree re-verification pending", "review finding 1: references/merge-and-recovery.md keeps a stale sentence claiming post-merge applies the changed-path criterion", "review finding 2: reconcile.py still calls evidence_verify with the default active phase, so a merged delivery can still not reach PASS under reconcile", "review finding 3: observed_at_commit is mandatory in the finalized phase, so historical-shaped post-merge evidence gains two errors per report"]}
```
