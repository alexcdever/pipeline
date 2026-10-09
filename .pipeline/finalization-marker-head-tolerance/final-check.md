# Final check

主代理最终检查（第三层验证）。

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1 | PASS | `39c8984` / `c677340` |
| 独立审查 | **PASS**（并发现引用卫生问题） | `e0199a8` |
| 执行 round 2（修证据引用） | PASS | `4a8518` |
| 主代理最终检查（本轮） | PASS | 本文件 |

## 本任务修的缺陷

`pipeline_tools/core.py` 的 `verify_finalization_snapshot` 原先要求最终化标记的 `identity.head` 严格等于当前 HEAD，而**提交标记本身就会推动 HEAD**——循环不可满足。已合并且闸门 PASS 的交付，提交标记后 `evidence verify --phase finalized` 报 `finalization head is stale`；既有 16 个历史标记同样受此影响。

修法：head 允许被"仅本任务证据提交"推进（复用既有 `head_advanced_by_evidence_only`）；`branch`/`worktree` 仍严格相等；retention 快照判据不动；重复 `evidence-finalize` 仍返回 `finalized`。

**执行者的承重证据**：把 `core.py` 单独回退后验收1 立刻失败并报 `['finalization head is stale']`。**审查的承重证据**：独立把 `core.py` 换成基线版本重跑同一条链，得到同样失败；还原后 sha256 与 HEAD 一致。

## 本轮主代理亲自做的事

1. **身份核对**：任务分支 `fe72596 → 39c8984 → c677340 → e0199a8 → 4a8518`；主工作树未被动过。
2. **重跑四条验收**：逐条退出码 0。
3. **重跑全量测试**：`395 passed, 28 subtests passed`，退出码 0（基线 392 + 3 新增）。
4. **独立复验两个方向**：直接调用 `verify_finalization_snapshot`——标记提交后（仅证据路径前移）返回 `[]`；产品路径改动后返回 `['finalization head is stale']`。
5. **范围与卫生**：`fe72596..39c8984` 共 3 个路径，全在范围内；禁止路径（含三个依赖任务证据目录、历史证据、`docs/goal.md`）零改动。

## 未验证项

- 合并后主工作树复验未进行——post-merge 硬要求，合并后会重跑并更新本文件与 `final-result.json`，随后提交 `finalization.json` 并执行 `--phase finalized` 校验。
- 既有 16 个 `finalization.json` 在新判据下的通过数未枚举。
- **仓库级已记录问题**：较早的报告里有 23 处不可解析的根相对 `evidence_refs`（不阻塞最终化，但会让 `--phase finalized` 报噪声）。本任务的执行与审查证据已全部改用可解析引用；历史报告属历史，不重写。

## 结论

三层验证全部通过，范围与历史完好。**READY-TO-MERGE。**

```pipeline-evidence
{"schema": 2, "task_id": "finalization-marker-head-tolerance", "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "branch": "finalization-marker-head-tolerance", "role": "main-final", "round": 1, "status": "PASS", "head": "39c8984b98dee0cd5669d5e670547e777bee794b", "sheet_revision": 1, "sheet_sha256": "b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76", "observed_at_commit": "39c8984b98dee0cd5669d5e670547e777bee794b", "generated_at": "2026-10-09T00:46:40Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_is_still_stale_after_product_commits", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_marker_snapshot_mismatch_is_still_rejected", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check fe72596..39c8984", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --name-only fe72596 39c8984", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-marker-head-tolerance", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["all four contract acceptance commands re-run by the main agent at implementation head 39c8984 with exit code 0", "main agent full suite re-run: 395 passed, 28 subtests passed, exit code 0", "the main agent independently reproduced both directions of the marker head rule: after the marker commit with evidence-only advancement verify_finalization_snapshot returns an empty error list; after a product-path commit it returns finalization head is stale", "three changed paths between the contract baseline and the implementation all fall inside the revision 1 allowed_paths; zero forbidden-path changes", "compileall exit code 0 and git diff --check exit code 0 over the implementation range"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["post-merge main-worktree re-verification pending", "the repo-wide pattern of unresolvable root-relative evidence_refs in older reports is recorded but not fixed here"]}
```
