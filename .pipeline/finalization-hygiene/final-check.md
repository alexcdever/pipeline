# Final check

主代理最终检查（第三层验证）。

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1（代码：剪枝豁免 + 范围放宽） | PASS | `f211892` |
| round 1 审查 | PASS | — |
| **范围修订**：两处陈旧文档入范围（revision 1→2） | — | `06ff204` |
| 执行 round 2（文档同步） | PASS | `21e8168` / `07679fc` |
| round 2 审查 | **PASS** | `4857e36` |
| 主代理最终检查（本轮） | PASS | 本文件 |

## 本任务修的两处卫生问题

- **A** 最终化不再删除本地状态文件：`goal.json` 与 `amendments.json` 被豁免，与保留集一并留下；其余非保留文件照旧剪掉（反向验证：把剪枝改回只认保留集，验收1 立刻失败）。
- **B** "仅证据提交"的范围由"本任务证据目录"放宽到 `.pipeline/**` 全域 + metrics，于是别的任务提交证据不再让已关闭任务失效；混合提交与不可解析路径保持 fail-closed（反向实验证明判据不可移除）。

## 本轮主代理亲自做的事

1. **身份核对**：任务分支 `e75c787 → f211892 → 44444ba → d002c23 → 21e8168 → 07679fc → 4857e36`；主工作树未被动过。
2. **重跑四条验收**：逐条退出码 0。
3. **重跑全量测试**：`401 passed, 28 subtests passed`，退出码 0（基线 398 + 3）。
4. **独立复验范围判据**：直接调 `evidence_only_paths` 十一条探针——`.pipeline` 任意任务证据 / metrics / planning → True；产品 / 测试 / 文档 → False；**混合提交 → False**；绝对 / 空 / 穿越路径 → False。
5. **旧表述核对**：三类被推翻的措辞在 `references/` 与 `SKILL.md` 中已无匹配。
6. **范围与卫生**：`e75c787..21e8168` 共 11 个路径，全在 revision 2 范围内；禁止路径零改动；`compileall` 与 `git diff --check` 为 0。

## 未验证项与遗留

- 合并后主工作树复验未进行。
- **两处范围外措辞残留**（登记给后续文档统一）：`references/acceptance-evidence.md:66`（`evidence_freshness` 段仍写"落在证据目录内"，未点名 `.pipeline`）与 `references/compat-and-migration.md:13`（历史版本条目仍写"只改本任务证据"，属历史记录，不重写）。
- **版本与兼容条目纪律已中断**（近几轮行为变更未配 `compat-and-migration.md` 条目，`SKILL.md` 仍 `0.16.0`），登记给 T3 一并处理。

## 结论

三层验证全部通过，范围与历史完好。**READY-TO-MERGE。**

```pipeline-evidence
{"schema": 2, "task_id": "finalization-hygiene", "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "branch": "finalization-hygiene", "role": "main-final", "round": 2, "status": "PASS", "head": "21e81682cd0a46288da2263f9e92ab2183015f28", "sheet_revision": 2, "sheet_sha256": "65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e", "observed_at_commit": "21e81682cd0a46288da2263f9e92ab2183015f28", "generated_at": "2026-10-09T03:09:59Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check e75c787..21e8168", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "grep -rn \"只动本任务证据目录|只豁免任务自身证据|只有本任务证据\" references/ SKILL.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "expected_exit_code": 1, "exit_code": 1, "evidence_ref": "final-check.md"}], "assertions": ["all four contract acceptance commands re-run by the main agent at implementation head 21e8168 with exit code 0", "main agent full suite re-run: 401 passed, 28 subtests passed, exit code 0", "the main agent independently reproduced the widened scope: .pipeline paths of any task, metrics and planning are evidence-only; product, test and document paths are not; a mixed commit, an absolute path, an empty path and a traversal path all fail closed", "the three superseded wordings are gone from references and SKILL.md (grep exit code 1, no match)", "eleven changed paths, zero forbidden-path changes; compileall exit code 0 and git diff --check exit code 0"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["post-merge main-worktree re-verification pending", "two residual wordings outside this contract's scope are recorded for later documentation work"]}
```
