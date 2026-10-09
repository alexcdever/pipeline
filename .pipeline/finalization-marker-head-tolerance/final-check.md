# Final check

主代理最终检查，**合并后版本**。本文件在合并后于主工作树内重写并重跑，作为独立的 post-merge 证据提交。

## 合并信息

- 合并提交：`6f563e1821071c5a35c279adfc2b3b08799c7c4f`（`merge finalization marker head tolerance`），父提交 `fe72596`（main）与 `cf13d90`（任务分支尖端）
- 主工作树根：`D:/Projects/Skills/pipeline`

## 三层验证经过

| 阶段 | 结论 | 提交 |
|---|---|---|
| 执行 round 1 | PASS | `39c8984` / `c677340` |
| 独立审查 | **PASS**（并发现执行证据引用不可解析） | `e0199a8` |
| 执行 round 2（修证据引用） | PASS | `4a8518` |
| 主代理最终检查（合并前） | PASS，pre-merge 闸门通过 | `cf13d90` |
| 主代理最终检查（合并后，本轮） | PASS | 本文件 |

## 合并后本人在主工作树根重跑的内容

1. 四条契约验收测试：逐条退出码 0。
2. 全量测试：`395 passed, 28 subtests passed`，退出码 0（基线 367）。
3. 依赖可加载；`compileall` 与 `git diff --check` 退出码 0。

## 交付意义

`verify_finalization_snapshot` 原先要求标记的 head 严格等于当前 HEAD，而提交标记必然推动 HEAD——**循环不可满足**，`finalized verify` 从未在提交后成立过（既有 16 个标记同样受影响）。本任务让 head 允许被"仅本任务证据提交"推进，同时保持产品路径改动与快照失配 fail-closed。

**两重承重证据**：执行者把 `core.py` 单独回退后验收1 立即失败；审查者独立用基线版本重跑同一条链得到同样失败；主代理又独立调 `verify_finalization_snapshot` 复验了两个方向。

## 未验证项

- 本文件提交后才会写入最终化标记，随后执行 `evidence verify --phase finalized`。
- 既有 16 个 `finalization.json` 在新判据下的通过数未枚举。
- 仓库级已记录问题：较早报告里有 23 处不可解析的根相对 `evidence_refs`（不阻塞最终化，但会给 `--phase finalized` 带噪声）；历史报告不重写。

## 结论

worktree 通过且主工作树复验通过。**已合并，可最终化。**

```pipeline-evidence
{"schema": 2, "task_id": "finalization-marker-head-tolerance", "worktree": "D:/Projects/Skills/pipeline", "branch": "main", "role": "main-final", "round": 2, "status": "PASS", "head": "6f563e1821071c5a35c279adfc2b3b08799c7c4f", "sheet_revision": 1, "sheet_sha256": "b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76", "observed_at_commit": "6f563e1821071c5a35c279adfc2b3b08799c7c4f", "generated_at": "2026-10-09T00:51:58Z", "commands": [{"command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_is_still_stale_after_product_commits", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_marker_snapshot_mismatch_is_still_rejected", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -c \"import pipeline_tools.core, pipeline_tools.planning; print('imports ok')\"", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "python -m compileall -q pipeline_tools scripts tests", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}, {"command": "git diff --check fe72596..HEAD", "cwd": "D:/Projects/Skills/pipeline", "exit_code": 0, "evidence_ref": "final-check.md"}], "assertions": ["post-merge re-verification ran in the main worktree root after merging branch ref cf13d90 into main", "all four contract acceptance commands pass in the main worktree with exit code 0", "main worktree full suite passes: 395 passed, 28 subtests passed, exit code 0", "pipeline_tools modules import cleanly; compileall exit code 0; git diff --check exit code 0", "the merge is a real merge commit with parents fe72596 and cf13d90", "this delivery is what makes finalized verification satisfiable at all: committing the marker necessarily advances HEAD past the head the marker records"], "evidence_refs": ["final-check.md", "final-result.json", "executor-report.md", "review-report.md"], "unverified": ["finalization marker written in a following step", "the repo-wide pattern of unresolvable root-relative evidence_refs in older reports is recorded but not fixed here"]}
```
