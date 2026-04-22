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
5. Correlate active processes with the dirty paths and any issue-specific overnight work.
   - If an overnight agent is actively working an issue, avoid choosing a path that collides with that issue.
6. Report the result precisely:
   - which repo is clean
   - which repo is dirty
   - whether the dirt appears operational/generated vs implementation work
   - whether an active background agent makes the state unsafe to touch
7. Recommend the next task based on lowest contention, not just highest priority.

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