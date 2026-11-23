# Skills Unification Stream — Exit Report

## Stream Started
Issue #1941: "hermes should be conscious to write skills etc. to .claude to make it seamless to use claudecode"

## Problem Statement
Hermes was creating skills in ~/.hermes/skills/ but Claude Code couldn't see them (reads from .claude/skills/). 
Skills, scripts, hooks, and rules created by Hermes during sessions were invisible to CC, Codex, and Gemini sessions.

## Solution Architecture
Repo .claude/skills/ is the single source of truth. 
- Hermes writes directly to .claude/skills/ via skill_manage
- External_dirs in config.yaml include all 6 repos' .claude/skills/ paths
- Hermes reads skills from repos via external_dirs (no local copies needed)
- Claude Code reads .claude/skills/ natively
- Codex reads .codex/skills/ which symlinks to ../.claude/skills/
- Gemini reads .gemini/skills/ which symlinks to ../.claude/skills/
- backfill-skills-to-repo.sh detects and prevents future drift
- Memory health-check cron at 05:50 daily monitors quality
- Staleness alert warns if bridge hasn't run in 48h

## Work Completed (14 of 15 issues closed)

### CLOSED
- #1941: hermes write-back strategy design
- #1942: migrated 91+ Hermes-only skills to .claude/skills/ (525+ files)
- #1943: backfill-skills-to-repo.sh (273 lines, per-repo routing)
- #1944: eliminated dual-write model (repo is source of truth)
- #1945: scripts/hooks/rules write-back verified (N/A - all in repo)
- #1946: wired backfill into harness-update.sh pipeline
- #1947: verified skills load via external_dirs (1156 confirmed)
- #1948: per-repo routing in backfill script
- #1949: Codex .codex/skills/ symlink already fixed
- #1916: memory health-check cron added (05:50 daily)
- #1920: 48h staleness alert in check-memory-drift.sh
- #1950: backfill end-to-end test passed
- #1951: sub-repo skill access confirmed (all 6 repos)
- #1952: cleaned up empty ~/.hermes/skills/ dirs
- #1918: Windows auto-memory sync — MemoryBridgeSync scheduled task + cross-platform bridge (#1918)

### OPEN
- #1879: rebuild session-start-routine skill
- #1917: memory backup and rollback mechanism
- #1919: memory ecosystem quick-reference card
- #1977: consolidated future tracking (contains #1917, #1919)

## Verification Results

### Skill Accessibility Matrix
| Agent | Mechanism | Workspace Hub | Total Across Repos |
|-------|-----------|---------------|-------------------|
| Claude Code | .claude/skills/ (native) | 696 | 974+ |
| Codex | .codex/skills/ -> symlink | 696 | 974+ |
| Gemini | .gemini/skills/ -> symlink | 696 | 974+ |
| Hermes | external_dirs (6 paths) | 696 | 974+ |

### File System State
- ~/.hermes/skills/: 0 SKILL.md files (all via external_dirs)
- .codex/skills/: symlink to ../.claude/skills/
- .gemini/skills/: symlink to ../.claude/skills/
- All 6 repos have proper .claude/skills/ structure
- backfill-skills-to-repo.sh prevents future drift

### Cron State
- 05:50 daily: memory-health-check (eval-memory-quality.py)
- 04:00 daily: memory bridge (bridge-hermes-claude.sh)
- Nightly: harness-update.sh includes backfill step

## Next Steps (Future Issues)

See #1977 for consolidated tracking of remaining memory ecosystem work:
1. #1917: memory backup/rollback mechanism
2. #1919: quick-reference card
3. #1879: session-start-routine skill rebuild
5. #1583: Hermes config parity validation
6. #1679: push notifications for harness failures
7. #1720: cross-agent session corpus audit

## Key Commits
- c231646e: migrated 2 unique Hermes-only skills to repo
- 00682a6e: hermes backfill 2 skills to .claude/skills/
- dc588c5e: test: revert dummy backfill test skill
- 8fb5cc28: hermes: backfill 1 skills to .claude/skills/
- d98a85bd: chore(cron): add memory-health-check task
- Multiple: backfill auto-commits during testing

All changes pushed to origin/main.
