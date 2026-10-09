# Archived Skill: `interactive-claude-to-file-based-fallback`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/interactive-claude-to-file-based-fallback`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/interactive-claude-to-file-based-fallback`
Consolidation date: 2026-04-29

---

---
name: interactive-claude-to-file-based-fallback
description: Switch from tmux/interactive Claude Code to file-based claude -p execution when interactive runs fail with upstream errors or analysis-only stalls, then verify landing from git/GitHub state.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [claude-code, workspace-hub, worktree, issue-execution, fallback, verification]
---

# Interactive Claude to File-Based Fallback

## When to use

Use this when:
- the user prefers tmux + interactive Claude Code first
- you are executing a plan-approved GitHub issue in `workspace-hub` or a similar repo
- interactive Claude repeatedly fails to make write-phase progress
- the repo or parent checkout may already be dirty, so you need worktree-safe verification after the run

## Why this exists

A recurring failure mode is that interactive Claude works well for planning and approval-safe prep, but can fail during implementation in two different ways:
- immediate upstream errors such as `API Error: 500` / `Internal server error`
- long context-gathering sessions that never transition into file writes, even after narrower retry prompts

In those cases, continuing to retry interactive mode wastes time. The productive move is to switch to file-based `claude -p` execution with a self-contained prompt, then verify success from actual git/GitHub state.

## Default decision ladder

1. Honor the user's preferred interactive tmux flow first.
2. If the run fails immediately, retry once with a narrower scope or alternate model if appropriate.
3. If the run stalls in analysis mode or fails again, switch to file-based execution.
4. Verify landed state using commit/issue/remote checks instead of trusting runner narration.

## Stall indicators that justify switching

Treat these as evidence that interactive mode is not productive for the current issue:
- prompt accepted, context loaded, but no file writes after extended monitoring
- repeated retries with tests-only or single-file prompts still do not create files
- multiple runs show the same pattern of long analysis with no commit activity
- the issue is implementation-ready, but only planning/read-only artifacts get produced reliably

## File-based execution pattern

Create a self-contained prompt file with:
- issue number
- approved plan path
- review artifact paths
- owned paths
- forbidden paths
- exact validation commands
- closeout instructions

Run non-interactively:

```bash
cd /mnt/local-analysis/workspace-hub
PROMPT=$(< docs/reports/<issue>-execution-prompt.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/<issue>-run.log
```

For approval-safe planning/read-only work:

```bash
claude -p --permission-mode plan --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/<issue>-plan.log
```

## Verification checklist after file-based execution

Always verify all three surfaces:

1. GitHub issue state
- `gh issue view <issue> --json state,comments,labels`

2. Commit reality
- `git show --stat --name-only <commit>`
- ensure the claimed owned files are actually in the commit

3. Remote vs parent-checkout state
- `git fetch origin`
- confirm whether the commit landed on `origin/main`
- separately inspect the user's parent checkout with:
  - `git status --short`
  - `git rev-list --left-right --count HEAD...origin/main`

Important rule:
- remote landed state and parent-checkout sync state are different truths
- if the remote landed but the parent checkout is dirty and behind, report that explicitly and do not claim the local repo is fully synced

## Worktree recommendation

If the parent checkout is dirty:
- execute from a clean issue worktree when possible
- do not auto-sync or pull the dirty parent checkout unless the user asks for reconciliation
- if needed, inspect/validate the landed commit from the clean worktree or a fresh detached worktree based on `origin/main`

## Reusable example outcome

Observed successful pattern:
- user preferred interactive tmux + `claude --dangerously-skip-permissions`
- interactive runs repeatedly stalled or failed with upstream errors during implementation
- switched to file-based execution for the same approved issue
- verified the landed implementation through targeted tests, scheduler validation, generated sample artifacts, and GitHub issue closure
- reported separately that `origin/main` had the landed commit while the local parent checkout remained dirty/behind

## Pitfalls

- burning multiple extra interactive retries after the same no-write stall pattern is clear
- assuming an issue is incomplete just because the parent checkout is behind; first verify remote landing
- claiming the local repo is synced when only the side worktree or remote branch is updated
- trusting the runner summary without checking the actual commit and issue state
