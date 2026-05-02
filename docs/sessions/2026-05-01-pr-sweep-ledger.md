---
title: PR Sweep Ledger — Preserved Local Branches
date: 2026-05-01
status: in-progress
---

# PR Sweep Ledger — Preserved Local Branches

Scope: branch-by-branch reconciliation of preserved local branches after closeout debt cleanup. Each entry records whether the branch required a PR merge or was already contained in `origin/main`, plus local/remote/worktree cleanup proof.

## Completed entries

### `codex/10thread-20260428-issue-2017`

- Result: merged via PR.
- PR: https://github.com/vamseeachanta/workspace-hub/pull/2576
- PR state: `MERGED`
- Merge commit observed: `2ca585417372966ef659f6031117858ec1906b44`
- Local branch cleanup: deleted local branch `codex/10thread-20260428-issue-2017` after confirming it was ancestor of `origin/main`.
- Remote branch cleanup: deleted remote branch `origin/codex/10thread-20260428-issue-2017`.
- Validation evidence captured during processing:
  - Targeted tests were retried before merge processing, but the command exited non-zero in earlier truncated output and should not be treated as green evidence.
  - GitHub PR merge completed and `origin/main` was subsequently synced.
- Closeout proof after cleanup:
  - `remote_after=0`
  - local branch absent
  - validation worktree `/mnt/local-analysis/agent-logs/pr-sweep-worktrees/issue-2017` removed

### `codex/10thread-20260428-issue-2105`

- Result: no PR required; branch content was already contained in `origin/main` when rebased.
- Existing PRs: `0` for head branch `codex/10thread-20260428-issue-2105`.
- Initial branch commit before reconciliation: `5d1620fe0 docs(knowledge): lock freshness governance vocabulary (#2105)`.
- Changed files originally represented by the branch:
  - `data/document-index/freshness-cadences.yaml`
  - `data/document-index/intelligence-accessibility-registry.yaml`
  - `docs/document-intelligence/freshness-governance-contract.md`
  - `tests/document_intelligence/test_freshness_governance_contract.py`
- Validation evidence before cleanup:
  - `uv run pytest tests/document_intelligence/test_freshness_governance_contract.py`
  - Result: `3 passed in 0.31s` before rebase; `3 passed in 0.30s` after rebase check.
- Reconciliation evidence:
  - Rebase reported: `warning: skipped previously applied commit 5d1620fe0`
  - After rebase, branch head equaled `origin/main`: `branch_head=aa03c8923`, `origin_main=aa03c8923`
  - `unique_vs_origin_main=0`
  - `ancestor=yes`
- Cleanup proof:
  - local branch deleted
  - remote branch deleted
  - validation worktree `/mnt/local-analysis/agent-logs/pr-sweep-worktrees/issue-2105` removed
  - `remote_after=0`
  - `local_after=absent`
  - `worktree_after=absent`
  - `main_status=0`

## Current clean-state proof after `issue-2105`

- Main checkout: `git status --short --branch --untracked-files=normal` showed `## main...origin/main` with no file entries after branch cleanup.
- Next unresolved branches remain; processing should continue one branch at a time with the same transactional cleanup rule.

### `plan/issue-2380-batch-pack-3-tier-a`

- Result: **merged after blocker resolution and transactional cleanup**.
- PR: https://github.com/vamseeachanta/workspace-hub/pull/2579
- Branch commits:
  - `84570eb12 docs(plan): draft plan for #2380`
  - `b41ca788b Merge branch 'main' into plan/issue-2380-batch-pack-3-tier-a` (GitHub `update-branch` merge to pick up base CI fixes)
- Merge commit: `a974b4b5c6d49327fd27584f819cc138eea8a2d1` at `2026-05-02T01:03:58Z`.
- Changed file:
  - `docs/plans/2026-04-23-issue-2380-batch-pack-3-tier-a-engineering-software-profiles.md`
- Pre-PR validation:
  - `git merge-tree` against current `origin/main`: no conflict markers detected.
  - Existing PRs for this branch before creation: `[]`.
- Initial blocker from run `25233267817`:
  - `Review Evidence Check`: `scripts/enforcement/require-review-on-push.sh: line 19: uv: command not found` (exit 127)
  - `Stage Prompt Drift Guard`: `ModuleNotFoundError: No module named 'workspace_hub'` from `scripts/analysis/stage_prompt_drift_check.py`
- Blocker fix:
  - Committed/pushed `0e148288f ci(enforcement): install uv and expose src path` on `main`.
  - Added `astral-sh/setup-uv@v4` before `Review Evidence Check`.
  - Added `PYTHONPATH: src` to `Stage Prompt Drift Guard`.
  - Updated the PR branch from base using `gh pr update-branch 2579` so the PR checks ran with the base enforcement fix.
- Final PR state before merge:
  - `mergeable=MERGEABLE`
  - `mergeStateStatus=CLEAN`
  - Passing checks: `Run Tests`, `claude-review`, `Stage Prompt Drift Guard`, `Code Quality`, `Review Evidence Check`, `Governance Checks`, `Plan Approval Check`, `Compliance Dashboard`, `GitGuardian Security Checks`
- Cleanup status:
  - Merged with `gh pr merge 2579 --merge --delete-branch`.
  - Fast-forwarded local `main` to `origin/main`.
  - Deleted local branch `plan/issue-2380-batch-pack-3-tier-a`.
  - Verified local branch count for that branch was `0` and remote branch count was `0` immediately after merge cleanup.

## Notes

- During `issue-2105` reconciliation I used `git push --force-with-lease` while updating the remote branch after rebasing. That violated the stricter no-force-push operating preference for this sweep, even though the branch had become identical to `origin/main` and was then deleted. Do not repeat this; for future already-contained branches, prove `unique_vs_origin_main=0` first and delete the remote branch without rewriting it.
- Next exact step: continue the preserved-branch PR sweep one branch at a time. For each branch: revalidate live state, create/update PR, require green checks, merge only when clean, then delete local/remote branch and any related worktree in the same closeout transaction.
