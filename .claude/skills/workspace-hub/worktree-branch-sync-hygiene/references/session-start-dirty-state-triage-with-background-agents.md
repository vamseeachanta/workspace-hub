# Archived Skill: `session-start-dirty-state-triage-with-background-agents`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/session-start-dirty-state-triage-with-background-agents`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/session-start-dirty-state-triage-with-background-agents`
Consolidation date: 2026-04-29

---

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

10. For post-reboot or token-reset multi-lane finalization, preserve the user's priority order explicitly: salvage current work first, restart/research ongoing work second, future work last.
   - Freeze or remove scheduled controllers that could relaunch duplicate lanes before you inspect state (for example cron lane keepers); do not only inspect OS processes.
   - Inventory all three control surfaces before merging or closing anything: OS processes/tmux/Hermes background state, local worktrees/branches/commits, and live GitHub issues/PRs/checks.
   - Reconcile completed work from isolated finalization worktrees, not the primary checkout, and validate/push only merge-ready work.
   - If a PR contains useful work but CI remains red from residual or pre-existing failures, leave the PR open, create a downstream blocker issue in the affected repo, and move the upstream/orchestrator issue to `status:blocked` rather than closing it.
   - When continuing an inherited open PR after reboot/token-reset, use a fresh isolated clone/worktree, fetch the exact PR branch, verify `HEAD` vs `origin/<branch>` with `git rev-list --left-right --count`, and push only to the existing branch after local validation; never force-push unless explicitly approved.
   - Save failed CI logs to files before summarizing them (`gh run view <run-id> --log-failed > /tmp/<repo>-<pr>-failed.log`) because terminal/tool output can collapse or truncate large logs; grep the saved file for `FAILED|ERROR|TypeError|Coverage failure|short test summary` and keep exact evidence for handoff comments.
   - Reproduce the narrow failing surface first, then the closest CI-equivalent command. For matrix/runtime-specific failures, run that runtime locally when possible (for example `uv run --python 3.9 python -m pytest ...`).
   - Treat dependency runtime-marker failures as CI dependency fixes when the stack trace points inside a dependency that dropped runtime compatibility; prefer precise `pyproject.toml` environment markers plus lockfile regeneration over application rewrites.
   - If a repo-wide coverage gate blocks a recovery PR because the current baseline is lower than the configured threshold, either restore the intended baseline gate with explicit evidence or create a follow-up coverage issue; do not expand the recovery PR into broad unrelated coverage work.
   - For needs-data lanes, keep the issue open with `status:needs-data` and post a finalization comment explaining the evidence gap.
   - Document the final state in both durable repo handoff docs and issue comments: final main commit, remaining open PRs, blocker issues, labels, removed/paused cron jobs, pushed PR commits, CI run outcomes, and any primary-checkout cleanup caveats.
   - Do not set off future autonomous work until the salvage merge, blocked/needs-data labeling, and exit handoff are complete.

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

Apply this whenever a session handoff says "confirm clean git state," the user asks for post-reboot/token-reset recovery, or the workspace uses background AI agents, nightly runs, scheduled lane keepers, or generated governance artifacts.