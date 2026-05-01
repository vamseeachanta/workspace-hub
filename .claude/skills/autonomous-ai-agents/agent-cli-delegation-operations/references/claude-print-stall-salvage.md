# Archived Skill: `claude-print-stall-salvage`

Original path: `/home/vamsee/.hermes/skills/autonomous-ai-agents/claude-print-stall-salvage`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/autonomous-ai-agents/claude-print-stall-salvage`
Consolidation date: 2026-04-29

---

---
name: claude-print-stall-salvage
description: Recover delegated Claude Code print-mode runs that stall silently or produce partial edits in large worktrees.
version: 1.0.0
tags: [claude, delegation, print-mode, stall, recovery, worktree]
---

# Claude Print-Mode Stall Salvage

Use when a delegated `claude -p` implementation run is launched in a worktree and appears to hang with little/no stdout, an empty tee log, or long-running internal shell scans.

## Trigger signs

- `claude -p ... | tee <log>` has an empty or near-empty log for several minutes.
- The process is still running, but the log is not growing.
- `ps` shows Claude or a child process running a broad command such as `rg`, `git status`, or repo-wide scans.
- `git status --short -- <owned paths>` shows useful partial edits despite no final Claude summary.
- The delegated run has exceeded the expected wall-clock budget for a bounded issue.

## Recovery workflow

1. Inspect state before killing:
   - `find tmp/claude-logs -type f -printf '%f %s bytes\n'`
   - `ps -ef | grep '<worktree-or-prompt-id>' | grep -v grep`
   - `git status --short -- <owned paths>`

2. If useful partial edits exist and stdout is still stalled, stop the delegated run:
   - kill the tracked Hermes background process if available, or kill the exact Claude subprocess/process group.
   - If Claude is stalled inside a child command such as `git push`, inspect `ps -eo pid,ppid,pgid,stat,comm,args` first and terminate exact PIDs/negative PGIDs; avoid `pkill -f` patterns that can match the invoking shell and kill the recovery command itself.
   - preserve in-scope edits; do not reset the worktree blindly.

3. Verify path contract immediately:
   - `git status --short`
   - confirm only approved/owned paths changed.
   - remove or revert runtime artifacts/logs unless they are explicitly in scope.

4. Finish centrally if the remaining work is small:
   - inspect the partial diff.
   - complete only the approved scope.
   - run the exact targeted validator from the approved plan.

5. Run independent review before landing:
   - include that Claude produced partial work but stalled.
   - ask reviewer to check scope, acceptance coverage, and path-contract compliance.

6. In closeout, be transparent:
   - execution mode was delegated/hybrid.
   - Claude produced initial partial work but stalled.
   - orchestrator completed recovery, verification, commit/push, and closeout.

## Important details

- Do not judge a `claude -p` run by stdout alone. Verify with git/file state.
- Do not let a stalled delegated process monopolize the worktree indefinitely.
- Prefer preserving good partial edits over restarting from scratch when the path contract is clean.
- If a repo-wide Python test or scan is slow because it walks ignored/untracked/generated files, prefer tracked-file approaches such as `git ls-files` or `git grep` in tests and validators.

## Example checks

```bash
find tmp/claude-logs -type f -maxdepth 1 -printf '%f %s bytes\n' | sort
ps -ef | grep '/mnt/local-analysis/worktrees/ws-2311-exec' | grep -v grep
git status --short -- tests/docs/test_stage_transition_reference_confinement.py tests/helpers/stale_reference_docs.py
```

## Closeout wording pattern

```text
Execution mode: delegated/hybrid. Claude was launched in isolated worktree <path> and produced the initial targeted helper/test work. The non-interactive run stalled with no useful stdout, so the orchestrator stopped it, preserved in-scope partial edits, completed the minimal remaining changes, ran validation/review, committed, pushed, and closed.
```
