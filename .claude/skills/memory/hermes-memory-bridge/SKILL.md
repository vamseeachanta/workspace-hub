---
name: hermes-memory-bridge
description: Architecture and scripts for syncing Hermes memory into git-tracked .claude/memory/ so all machines get context via git pull. Covers quality gate, drift detection, topic mirroring, and cron automation.
tags: [memory, hermes, cross-machine, context-parity, bridge]
created: 2026-04-05
---

# Hermes Memory Bridge

## Problem

Hermes writes memory to `~/.hermes/memories/` (Linux only). Claude Code writes to `~/.claude/projects/*/memory/` (per-machine, not portable). Non-Hermes machines (Windows licensed-win-1) have zero context. Without a bridge, every machine operates with different knowledge.

## Architecture: Memory Lives In The Repo

Instead of sync tools or tarballs, memory files are committed to `.claude/memory/` inside the workspace-hub repo. Git IS the sync mechanism.

```
Hermes memory (~/.hermes/memories/)
  → pre-bridge-quality.sh (quality gate)
    → bridge-hermes-claude.sh (injects into repo memory files)
      → .claude/memory/ (git-tracked)
        → git push
          → any machine: git pull → gets same context
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/memory/bridge-hermes-claude.sh` | Main bridge: reads Hermes memory, injects into agents.md via template, mirrors Claude topic files |
| `scripts/memory/pre-bridge-quality.sh` | Quality gate: checks char limits, stale entries, duplicates, content richness. Scored 0-100. ≤50 blocks bridge, 50-70 warns+bridges, 70+ passes |
| `scripts/memory/check-memory-drift.sh` | Drift detection: compares Hermes memory against repo agents.md. Exits 0/1. `--fix` runs bridge |
| `scripts/memory/bootstrap-machine.sh` | One-time setup for new machines: creates ~/.claude/CLAUDE.md |

## Repo Memory Files

| File | Content |
|------|---------|
| `.claude/memory/agents.md` | User profile, AI subscriptions, workflow rules, Hermes-injected facts |
| `.claude/memory/context.md` | Machine conventions, paths, Python rules, workspace layout, legal compliance |
| `.claude/memory/claude-auto-memory.md` | Snapshot of Claude auto-memory MEMORY.md index |
| `.claude/memory/topics/` | 19 mirrored Claude topic files (feedback_*, working-style, etc.) |
| `.claude/memory/templates/agents-template.md` | Template for agents.md with BRIDGE injection markers |

## BRIDGE Marker Pattern

agents.md uses `<!-- BRIDGE:START -->` / `<!-- BRIDGE:END -->` markers in a template:
```
# Agent Workflow Facts
> Git-tracked template file

<!-- BRIDGE:START -->
## Synced from Hermes Memory (date)
- bullet 1
- bullet 2
<!-- BRIDGE:END -->

---
## User
... hardcoded baseline that doesn't change ...
```

The bridge script reads the template, injects Hermes content between markers, and writes the result. This prevents duplication — baseline lives in template, dynamic content lives in bridge injection.

## Quality Gate Scoring

Score starts at 100, deductions:
- Memory file missing: -30
- Memory file empty: -25
- Exceeds char limit (2200 MEMORY.md / 1375 USER.md): -20 per file
- Approaching limit (>90%): -5 per file
- Stale entries (>90 days old): -3 per entry
- Duplicates between MEMORY.md and USER.md (>2): -5
- Nearly empty (<200 chars): -15

Score ≤50: BLOCK bridge (critical failure)
Score 50-70: WARN and bridge (or --fix mode auto-compacts first)
Score ≥70: PASS, bridge runs normally

## Cron Job

Hermes cron `8c797470d7d3` (memory-bridge-daily, 0 4 * * *):
1. Runs check-memory-drift.sh — skips bridge if in sync
2. Runs pre-bridge-quality.sh --fix — gates quality
3. Bridge commits + pushes (with stash/rebase for dirty working dir)

## Pitfalls

- Repo topology changes are high-priority bridge facts. If a session confirms that tier-1 repos moved between nested and sibling layouts, run `check-memory-drift.sh` and bridge the fact into `.claude/memory/agents.md`; otherwise Hermes may know the topology while repo-local agents still follow stale path assumptions.
- Existing quality scripts (compact-memory.py, curate-memory.py, eval-memory-quality.py) are BUGGY — wrong default paths, metrics calibrated for work-queue format not §-delimited memory. Use pre-bridge-quality.sh instead.
- The bridge must handle dirty working dir: stash before `git pull --rebase`, restore after push.
- Scheduled bridge jobs can collide with `scripts/repository_sync` or another Git process holding `.git/index.lock`; if `check-memory-drift.sh`, `git status`, or bridge preflight times out while a `git add`/sync process is active, inspect the owning process, wait briefly for the lock to clear, then rerun drift detection before deciding whether to bridge. Do not remove `.git/index.lock` unless the owning Git process is gone.
- If `pre-bridge-quality.sh --fix` generates bridge changes, stashes them, then exits nonzero because the internal commit sees `nothing to commit, working tree clean` or `nothing added to commit but untracked files present`, recover by checking out only `.claude/memory` from the generated `pre-bridge-stash`, staging `.claude/memory`, committing only `.claude/memory`, pushing, and then rerunning `check-memory-drift.sh` to verify sync. Do not add unrelated untracked files just to make the bridge commit succeed. If `git push` says `Everything up-to-date`, verify `HEAD` equals `origin/main` / `@{u}` because hooks may already have pushed. If the generated stash also contains non-memory paths, preserve the stash after the memory commit instead of dropping it. See `references/pre-bridge-stash-recovery.md` for the exact recovery/verification command sequence.
- Memory topic snapshots can legitimately document merge-conflict marker strings inside fenced code blocks. If the commit hook blocks `.claude/memory/topics/*` with unresolved-marker findings, first verify the markers are forensic/example content, then add the per-line hook exemption suffix `# CONFLICT_MARKER_FORENSIC_OK` to the literal marker lines only; do not disable hooks or rewrite unrelated memory content.
- Template file must exist at `.claude/memory/templates/agents-template.md` or bridge falls back to raw output.
- Windows MINGW64: paths use `/d/workspace-hub/` format, not `D:\\`.

## Ecosystem Health Monitoring

`scripts/upkeep/health-check.sh` provides 16 automated checks:
1. Gateway status (critical if down — cron jobs won't fire)
2. Cron job count and state
3. Cron output freshness
4. Memory bridge freshness (last commit to .claude/memory/)
5. Memory drift (Hermes vs repo)
6-7. Hermes memory char limits (MEMORY.md / USER.md)
8-10. Disk space, ~/.hermes/ size, ~/.claude/ size
11. Repo unpushed commits
12-14. Sub-repo sync (digitalmodel, aceengineer-strategy, worldenergydata)
15-16. Claude topics count and auto-memory snapshot freshness

Exit codes: 0 = all pass, 1 = warnings, 2 = critical failures
Usage: `bash scripts/upkeep/health-check.sh` or `/today --health`

### Operational Findings

- Gateway can go DOWN without warning (found inactive for 7+ hours, cron jobs never fired)
- Memory approaches limits quickly (MEMORY.md hit 98% at 2170/2200 chars, USER.md hit 94% at 1291/1375)
- Quality gate thresholds are well-calibrated: memory at 90%+ triggers warning, forces attention
- Health check revealed gateway status as the most critical single point of failure — if Gateway is down, memory-bridge cron never runs, drift accumulates silently
