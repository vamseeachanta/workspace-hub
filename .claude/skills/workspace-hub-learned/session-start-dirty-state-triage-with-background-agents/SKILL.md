---
name: session-start-dirty-state-triage-with-background-agents
description: Distinguish real implementation dirt from generated session-state churn when resuming a repo with active overnight/background agents.
version: 1.0.0
category: workspace-hub-learned
tags: [session-start, git, background-agents, triage, workspace-hub]
---

# Session-start dirty-state triage with background agents

Use when a handoff or user asks you to confirm a repo is clean before resuming work, especially in workspace-hub where overnight Claude runs, governance hooks, and provider scorecards may keep the orchestrator repo dirty.

## Why this exists

A plain `git status` can overstate risk. In workspace-hub, dirty state may come from:
- `.claude/state/*` session and correction logs
- provider scorecard/report outputs under `config/ai-tools/` and `docs/reports/`
- transient directories like `.nightly-results/` or inspection scratch dirs
- an active overnight/background Claude run still writing state

Meanwhile a nested implementation repo (for example `aceengineer-website/`) may still be fully clean and ready.

## Workflow

1. Read the handoff first and extract any mentioned repos, issue numbers, and active parallel-agent warnings.
2. Check git state separately for each repo involved, not just the top-level workspace.
   - Example:
     - `git status --short --branch` in `workspace-hub`
     - `git status --short --branch` in `aceengineer-website`
3. If the top-level repo is dirty, classify the paths:
   - generated governance/session state
   - generated reports/scorecards
   - transient scratch/output dirs
   - real source/docs changes affecting the intended task
4. Check for active agent processes before concluding the dirty state is yours to clean up.
   - `ps aux | grep -E 'claude|codex|gemini' | grep -v grep`
   - Include interactive shells/agents, not only background jobs: `pwdx <pid>` can reveal an active `claude` sitting in the repo even after a reboot.
   - `process(action='list')` may be empty after reboot because Hermes-tracked background sessions do not survive, while OS-level Claude/Hermes/TUI processes may still exist.
5. Correlate active processes with the dirty paths and any issue-specific overnight work.
   - If an overnight agent is actively working an issue, avoid choosing a path that collides with that issue.
   - If an active interactive Claude process has cwd in the same repo, treat repo-wide Git mutation as unsafe even if no Hermes background sessions are listed.
6. For post-reboot salvage or stale-lock recovery, preserve state before any mutation:
   - create a backup branch at current `HEAD`, e.g. `git branch salvage/post-reboot-YYYYMMDD-HHMMSS HEAD`
   - save `git diff --binary`, `git diff --cached --binary`, and `git status --porcelain=v1` outside the repo or under a dated salvage directory
   - copy any key handoff/result file explicitly before reset/rebase/stash attempts
   - only remove `.git/index.lock` after confirming no live Git/agent process owns it or is working in the repo; a stale lock alone is not permission to mutate when an active Claude cwd is present
7. Report the result precisely:
   - which repo is clean
   - which repo is dirty
   - whether the dirt appears operational/generated vs implementation work
   - whether an active background/interactive agent makes the state unsafe to touch
   - where salvage artifacts were written if mutation is deferred
8. Recommend the next task based on lowest contention, not just highest priority.
   - If safe reconciliation is blocked by an active writer, schedule or hand off a delayed narrow reconciliation job that re-checks process/git state before mutating.

9. For post-reboot recovery where important commits/artifacts exist outside the dirty primary checkout, reconcile from an isolated clean worktree rather than touching the active checkout.
   - Create or use a throwaway reconciliation worktree from `origin/main` (for example `/mnt/local-analysis/reconcile-main-YYYYMMDD`).
   - Fetch the remote, cherry-pick/rebase only the recovered commits or copy only the recovered handoff/artifact files into that worktree.
   - Resolve shared planning-index conflicts there, preserving newer remote rows/status and adding only the missing recovered rows/artifacts.
   - Push the reconciled commit(s) from the clean worktree if verification passes.
   - Leave the primary dirty checkout untouched while any Claude/Hermes/TUI process has cwd there.
   - Separately schedule a delayed cleanup/reconcile job for the primary checkout that re-checks live processes and saves diffs before any reset/stash.
   - If the recovery also reveals queued plan-review or implementation work, schedule that as a separate future job from the clean worktree so salvage, restart/review, and future work are decoupled.

## Good output pattern

- `workspace-hub`: not clean; mostly generated state/report churn plus active overnight agent on #2348
- `aceengineer-website`: clean
- Recommendation: choose a non-colliding path like #2357 rather than #2348

## Pitfalls

- Do not say "both repos are clean" just because the implementation repo is clean.
- Do not assume top-level dirt means the user's requested work is blocked.
- Do not ignore active overnight agents; they can explain the churn and create issue-level contention.
- Do not collapse nested repos into one cleanliness judgment.

## Reuse trigger

Apply this whenever a session handoff says "confirm clean git state" and the workspace uses background AI agents, nightly runs, or generated governance artifacts.