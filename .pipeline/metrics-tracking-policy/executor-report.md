# Executor report

- task-id: `metrics-tracking-policy`
- worktree: `D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy`
- branch: `metrics-tracking-policy`
- round: 1
- role: executor
- baseline product head: `776d3d9609703b2220e0ed0856dc940de15a88cc`
- goal sha256: `9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f` (unchanged)
- task_type: `prerequisite`; risk: `medium`; project_type: `cli`

## Commands

| Command | Exit code | Assertion |
|---|---:|---|
| `python -m unittest discover -s tests` | 0 | 316 tests passed (312 baseline + 4 new), no regression |
| `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice` | 0 | neutral policy documented in `references/metrics-contract.md`; mandatory phrasing absent |
| `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice` | 0 | neutral policy documented in `references/compat-and-migration.md`; mandatory phrasing absent |
| `python -m unittest tests.test_cli.CLITests.test_repository_metrics_are_ignored_and_untracked` | 0 | `.gitignore` carries `.pipeline/metrics/`, `check-ignore` returns 0, `ls-files` empty |
| `python -m unittest tests.test_cli.CLITests.test_cli_suite_does_not_write_repository_metrics` | 0 | real auto-metrics CLI run leaves repository metrics snapshot byte-identical |
| `python -m pipeline_tools --format json task validate docs/tasks/metrics-tracking-policy.md` | 0 | frozen sheet still validates as `pass` |
| `git ls-files .pipeline/metrics/ \| wc -l` | 0 | 0 tracked metrics files after untracking |
| `git check-ignore -v .pipeline/metrics/event.json` | 0 | matches `.gitignore:7:.pipeline/metrics/` |
| `git diff --check` | 0 | no whitespace errors |

## Observed changes

**1. `references/metrics-contract.md` — mandatory-tracking rule neutralized**

- Line 3: replaced 指标文件**应纳入 Git 追踪，不应加入项目 `.gitignore`** with a neutral statement plus an explicit developer-choice principle: whether pipeline-created paths are tracked is the project developer's decision; the skill neither requires nor forbids it; Git use is for script validation and LLM intent context only.
- `进度日志不进入 Git` section: dropped the clause that metrics must be committed; the `.pipeline/metrics/` bullet now says tracking is the developer's choice. **Progress-log rule kept intact** (`-progress.jsonl` must not enter Git).
- The `两者不要混` line: removed 把 `.pipeline/metrics/` 加进 `.gitignore` 同样是违规.
- `测试隔离规则` section reworded: the invariant is now **the suite must not write into the repository's `.pipeline/metrics/` directory**, independent of tracking status. The old "被追踪的 .pipeline/metrics/ 历史保持不变 / `git status --short .pipeline/metrics/`" bullet was replaced by a direct file-name→content-hash snapshot requirement, because `git status` is blind to ignored files.
- `反馈边界` closing line made conditional on the project choosing to track.

**2. This repo opts for untracked**

- `.gitignore`: added `.pipeline/metrics/` (line 7).
- `git rm -r --cached .pipeline/metrics/` — 1435 files left the index; **no on-disk file deleted**. `git ls-files .pipeline/metrics/` → 0. On-disk file count preserved.

**3. Metrics tests made meaningful again**

- `tests/test_cli.py` (`test_workflow_command_automatically_records_tracked_metric`): `check-ignore --no-index` assertion changed from `assertNotEqual(returncode, 0)` (forbade the repo policy) to `assertIn(returncode, (0, 1))` — the test no longer forbids either choice.
- `tests/test_cli.py`: removed/renamed `test_cli_suite_leaves_tracked_metrics_unchanged` (vacuous once ignored) and added two real tests — `test_repository_metrics_are_ignored_and_untracked` and `test_cli_suite_does_not_write_repository_metrics`. The latter snapshots the repository metrics directory, runs a genuine auto-metrics CLI invocation, snapshots again, and asserts equality.
- `tests/test_acceptance_id_and_template_compliance.py`: the tautological `assertNotIn(".pipeline/metrics/` 加入 `.gitignore`", contract)` (document says 加进, so it could never fail) was replaced by a positive assertion on the new isolation wording, plus two new acceptance tests asserting the neutral policy is documented and the old mandatory phrasing is gone.
- `tests/test_cli.py` helper docstring updated: it no longer says "tracked history gains an untracked event".

## Untracking evidence

| Measure | Before | After |
|---|---:|---:|
| `git ls-files .pipeline/metrics/` | 1435 | 0 |
| on-disk files under `.pipeline/metrics/` | 1436 | 1437 |
| `git status --short .pipeline/metrics/` | 1 untracked file | empty (ignored) |
| staged deletions `^D  .pipeline/metrics/` | — | 1435 |

The on-disk count moved 1436 → 1437 because this run's own `pipeline-tools` invocations append `observed` metrics events. No pre-existing file was deleted or modified: an independent sorted name+sha256 manifest of the directory was computed before and after untracking and was identical (`d5db9a3b…` for the name list, `cce0b26e…` for the name→hash manifest).

## Scope

`git status --short` shows exactly 5 modified files, all inside `allowed_paths` (`references/`, `tests/`, `.gitignore`), plus **1435 staged deletions under `.pipeline/metrics/`** — the intended untracking. Those staged removals match the contract's `forbidden_paths` pattern `.pipeline/** existing history`; per the dispatch, the intent is that these removals are the deliverable and `forbidden_paths` means "do not rewrite existing evidence content", not "do not untrack metrics". Flagged here explicitly as a potential tooling conflict; no workaround was applied.

## Unverified

- Independent reviewer re-run, main-agent final check, and post-merge re-verification in the main worktree are not performed here.
- `README.md:16` still says `.pipeline/metrics/`（由工具自动生成并纳入 Git 追踪）. `README.md` is **outside `allowed_paths`**, so it was left untouched. This is a real residual inconsistency in the repo's own docs — see follow-up note below.
- `commit_history_check` / `scope history` were not run: the staged deletions are uncommitted, so history scanning would not yet see them.

```pipeline-evidence
{"schema":1,"task_id":"metrics-tracking-policy","worktree":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","branch":"metrics-tracking-policy","role":"executor","round":1,"status":"PASS","commands":[{"command":"python -m unittest discover -s tests","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_cli.CLITests.test_repository_metrics_are_ignored_and_untracked","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"},{"command":"python -m unittest tests.test_cli.CLITests.test_cli_suite_does_not_write_repository_metrics","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"},{"command":"python -m pipeline_tools --format json task validate docs/tasks/metrics-tracking-policy.md","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"},{"command":"git ls-files .pipeline/metrics/ | wc -l","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"},{"command":"git check-ignore -v .pipeline/metrics/event.json","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"},{"command":"git diff --check","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"executor-report.md"}],"assertions":["316 full-suite tests passed, exit 0 (baseline 312 + 4 new)","neutral developer-choice policy documented in references/metrics-contract.md and references/compat-and-migration.md","old mandatory-tracking phrasing (应纳入 Git 追踪 / 不应加入项目 .gitignore / 加进 .gitignore 同样是违规) absent from both reference files","progress-log rule (must not enter Git) preserved intact","git ls-files .pipeline/metrics/ returns 0; git check-ignore returns 0 against .gitignore:7:.pipeline/metrics/","on-disk metrics file count unchanged apart from events appended by this run's own pipeline-tools invocations; sorted name+sha256 manifest identical before/after untracking","no pre-existing on-disk metrics file deleted or modified","frozen task sheet still validates as pass; goal.md sha256 unchanged","git status --short shows only allowed_paths modifications plus the intended 1435 staged deletions under .pipeline/metrics/"],"evidence_refs":["executor-report.md","executor-result.json"],"unverified":["independent reviewer re-run","main-agent final check","post-merge re-verification in the main worktree","README.md:16 still asserts metrics are Git-tracked but is outside allowed_paths"],"identity":{"product_head":"776d3d9609703b2220e0ed0856dc940de15a88cc"},"recommendation":"ready_for_review"}
```