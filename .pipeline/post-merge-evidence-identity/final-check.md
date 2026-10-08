# Final check

主代理最终检查，**合并后版本**（第三层验证）。本文件在合并后于主工作树内重写并重跑，按项目规则作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`f403c6b9666831becec94266172ba225ff3fdd51`（`merge post-merge evidence identity`），父提交 `fe999dc`（main）与 `c391e40`（任务分支尖端）
- 合并输入：经 `git worktree list --porcelain` 确认过的 branch ref `post-merge-evidence-identity`
- 主工作树根：`D:/Projects/Skills/pipeline`

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1（rev 2 旧设计） | PASS | `8b1ba98` / `aeefd29` |
| **设计变更**：改用阶段分工（rev 3） | — | `360ec91` |
| 执行 round 2 | PASS | `f39d1f9` / `34c7fa5` |
| **范围补充**：CLI 入口入范围（rev 4） | — | `fe999dc` |
| 执行 round 3 | PASS | `270ebc0` / `b89f764` |
| 独立审查 | **PASS** | `0d29bb6` |
| 主代理最终检查（合并前） | PASS，pre-merge 闸门通过 | `c391e40` |
| 主代理最终检查（合并后，本轮） | PASS | 本文件 |

契约经两次 `task amend` 修订（2→3→4），每次登记了裁决与结构化差异；执行者旧证据按"验证面变更即作废"重做两轮。

## 合并后本人在主工作树根重跑的内容

1. 七条契约验收测试：逐条退出码 0。
2. 全量测试：`387 passed, 28 subtests passed`，退出码 0（基线 367）。
3. 依赖可加载：`pipeline_tools` 四个模块 import 正常。
4. `compileall` 退出码 0；`git diff --check fe999dc..HEAD` 退出码 0。
5. 变更范围：13 个文件。

## 本任务的交付意义

post-merge 阶段的证据身份改为只由**任务单 id + 修订版本**给出，合并本身不再使任何证据失效；`active` 阶段的提交绑定逐字保持不变（独立审查用改动前的代码对四种情形做了逐字节错误列表比对）。`reconcile` 的报告身份一致判据同步改为 `task_id` + `sheet_revision`。上一版无效设计的 `merged_task_branch_identity` 已移除。

## 未验证项与遗留发现

- 三条**非阻塞**发现登记为后续工作：①`references/merge-and-recovery.md` 有一句与新阶段分工矛盾的旧话；②`reconcile.py` 仍以默认 `active` 阶段调用 `evidence_verify`，合并后的交付在 `reconcile` 下仍达不到 PASS；③`observed_at_commit` 在 finalized 阶段为必需字段，历史形态证据因此每报告多两条错误。
- 遗留：`.worktrees/` 下四个任务 worktree 的清理与历史迁移一并留给后续归档任务。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "post-merge-evidence-identity", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 2, "status": "PASS", "head": "f403c6b9666831becec94266172ba225ff3fdd51", "sheet_revision": 4, "sheet_sha256": "c32e3c23c23cb830ff867374e1be927880700fc8cd21a88c0654eff1a7dc91a9", "observed_at_commit": "f403c6b9666831becec94266172ba225ff3fdd51", "generated_at": "2026-10-08T19:21:25Z", "commands": [{"command": "python -m pytest -q tests/test_evidence.py -k post_merge_identity_uses_task_id_and_revision_only", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_rejects_revision_mismatch", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_rejects_task_id_mismatch", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k post_merge_requires_main_worktree_reverification", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k pre_merge_commit_identity_is_not_weakened", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_identity_agrees_on_task_and_revision", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -c \"import pipeline_tools.core, pipeline_tools.reconcile, pipeline_tools.planning, pipeline_tools.task_lifecycle; print('imports ok')\"", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check fe999dc..HEAD", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref c391e40 into main", "all seven contract acceptance commands pass in the main worktree with exit code 0", "main worktree full suite passes: 387 passed, 28 subtests passed, exit code 0", "pipeline_tools modules import cleanly; compileall exit code 0; git diff --check exit code 0", "the merge is a real merge commit with parents fe999dc and c391e40", "post-merge identity is judged by task_id plus sheet revision only, which is why this merged delivery verifies"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["three non-blocking review findings are recorded for follow-up work", "finding 1: references/merge-and-recovery.md keeps a stale sentence claiming post-merge applies the changed-path criterion", "finding 2: reconcile.py still calls evidence_verify with the default active phase", "finding 3: observed_at_commit is mandatory in the finalized phase, so historical-shaped post-merge evidence gains two errors per report"]}
```
