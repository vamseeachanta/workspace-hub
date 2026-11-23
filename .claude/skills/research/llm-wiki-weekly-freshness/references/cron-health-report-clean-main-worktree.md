# Cron health reports from dirty or non-main checkouts

## Context
Recurring wiki-health/reporting jobs may be invoked from a live workspace checkout that is dirty or on a feature branch. The requested command can still be run there for operator evidence, but committing generated reports directly from that checkout risks sweeping unrelated local changes into the report commit or pushing from the wrong branch.

## Durable pattern
1. Run the requested health command in the requested working directory first, preserving the exact observed output for the final report.
2. Inspect branch and dirty state before staging anything.
3. If the checkout is dirty or not on `main`, create a temporary clean worktree from `origin/main` and rerun the report command there.
4. Commit only the generated report artifacts from the clean worktree.
5. Push the report commit to `main`.
6. Verify `HEAD == origin/main` for the pushed commit and show the committed report files.
7. Remove the temporary worktree/branch after verification.
8. In the final report, distinguish:
   - **requested-checkout findings**: what the user explicitly asked you to run and what it saw locally;
   - **committed-main findings**: what was actually committed and pushed to `main`.

## Why this matters
A dirty/non-main checkout can include uncommitted wiki domains or local-only pages that are not present on `main`. Reporting only the committed `main` artifact can hide issues seen by the requested run; reporting only the dirty-checkout artifact can falsely imply those issues were committed. Keep both evidence streams explicit.

## Minimal command shape
```bash
git status -sb --untracked-files=no
git fetch origin main --prune
git worktree list --porcelain | grep -qx 'worktree /tmp-or-local-clean-worktree' \
  && git worktree remove --force /tmp-or-local-clean-worktree
git worktree prune
git worktree add /tmp-or-local-clean-worktree origin/main
(
  cd /tmp-or-local-clean-worktree
  uv run scripts/knowledge/wiki_health_cron.py
  git switch -c chore/wiki-health-YYYY-MM-DD
  git add docs/reports/wiki-health/health-YYYY-MM-DD.json docs/reports/wiki-health/health-YYYY-MM-DD.md
  git commit -m "chore: wiki health report YYYY-MM-DD"
  git push origin HEAD:main
  git fetch origin main
  test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
)
git worktree remove /tmp-or-local-clean-worktree
```

Use a repo-local sibling path instead of `/tmp` when large checkouts or filesystem boundaries make worktree materialization expensive or flaky.
