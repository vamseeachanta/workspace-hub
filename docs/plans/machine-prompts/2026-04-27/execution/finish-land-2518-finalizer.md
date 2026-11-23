# Finish/Land #2518 Finalizer Prompt

You are a real Claude Code subagent operating in the actual workspace. Finish and land workspace-hub GitHub issue #2518 safely.

Repository: `/mnt/local-analysis/reconcile-main-20260427`
GitHub repo: `vamseeachanta/workspace-hub`
Issue: #2518 — `fix(review): harden plan-review fanout provider invocation`
Issue URL: https://github.com/vamseeachanta/workspace-hub/issues/2518

## Context

- A previous Claude subagent already created local commit `d197e8e9e2cc961e32f63173442ce8abf4d4f39a` with message `fix(review): harden plan-review fanout provider handling (#2518)`.
- A prior run stalled while pushing branch `reconcile/post-reboot-main-20260427`; do not resume stale pushes.
- Current local status may include generated `scripts/testing/coverage-results.json`; this is not part of #2518 and should be restored/left unstaged unless already clean.
- Scope boundary: only #2518 files/artifacts should be landed. Do not touch Codex burn worktrees, machine prompt docs, or unrelated issues.

## Required steps

1. `cd /mnt/local-analysis/reconcile-main-20260427`.
2. Inspect state: `git status --short --branch`, `git log --oneline -5`, `gh issue view 2518 --repo vamseeachanta/workspace-hub --json state,labels,url`.
3. If `scripts/testing/coverage-results.json` is the only dirty path, restore it. If other dirty paths exist, stop and report; do not overwrite unrelated work.
4. Verify local HEAD is the #2518 commit and parent is on current `origin/main`. Run `git fetch origin main --quiet`. If origin/main advanced, rebase this #2518 commit onto `origin/main` safely. Resolve only trivial non-overlapping conflicts; otherwise stop and report.
5. Run validation before push:
   - `git diff --check HEAD~1..HEAD`
   - `bash -n scripts/review/plan-review-fanout.sh scripts/review/tests/test_plan_review_fanout.sh scripts/review/tests/mocks/codex scripts/review/tests/mocks/gemini`
   - `bash scripts/review/tests/test_plan_review_fanout.sh`
   - `command -v shellcheck >/dev/null && shellcheck scripts/review/plan-review-fanout.sh || true` — record if shellcheck unavailable.
6. Push #2518 to `main` only as a normal fast-forward/no-force push: `git push origin HEAD:main`. If rejected, fetch/rebase once and retry only if clean and validation still passes. Never force-push.
7. Verify remote: `git fetch origin main --quiet`; confirm `git merge-base --is-ancestor HEAD origin/main` and record `git rev-parse HEAD`.
8. Post a closeout comment to #2518 with commit SHA, changed file summary, validation commands/results, and note that the stale push process was replaced by this finalizer.
9. Update labels: remove `status:working` and `status:plan-approved` if present; add `status:done` if it exists. Do not fail the whole task if a label is missing.
10. Close #2518 only after commit is confirmed on `origin/main`.

Final output: concise summary with issue URL, final state, commit SHA, validation evidence, and blockers. Do not create new cron jobs. Do not schedule future work.
