---
name: memory-bridge-operation
description: Manage the Hermes ↔ repo memory sync system — bridge, quality gate, compaction, health checks, and cron
---

# Memory Bridge Operation

Manage the Hermes ↔ repo memory sync system that propagates context across all machines.

## Architecture

Memory travels with the repository via git. Hermes memory (~/.hermes/memories/) is the source of truth on ace-linux-1. The bridge script reads it, writes into .claude/memory/ in the workspace-hub repo, commits, and pushes. Every other machine (Windows licensed-win-1, new clones) gets updated context via git pull. Gateway must be running for cron jobs to fire.

## Script Inventory

| Script | Purpose |
|--------|---------|
| scripts/memory/bridge-hermes-claude.sh --commit | Reads Hermes memory, injects into agents.md via BRIDGE markers, commits and pushes |
| scripts/memory/pre-bridge-quality.sh --fix | Quality gate (0-100 score) before bridge; auto-compacts if needed |
| scripts/memory/check-memory-drift.sh | Exits 1 if Hermes memory ahead of repo, 0 if in sync |
| scripts/memory/bootstrap-machine.sh | Creates ~/.claude/CLAUDE.md on new machine, OS-aware |
| scripts/upkeep/health-check.sh --save | 16-check report: gateway, cron, memory, disk, repo sync, Claude topics |

## Cron Jobs

- memory-bridge-daily: 04:00 daily (job 8c797470d7d3) — runs pre-bridge-quality.sh --fix which calls bridge internally
- Gateway must be active (systemctl is-active hermes-gateway.service) or cron jobs won't fire

## Memory Compaction

Hermes memory has hard limits: MEMORY.md = 2200 chars, USER.md = 1375 chars. When approaching 90%+, compact before bridging.

### Manual Compaction Steps

1. Check current sizes: `wc -c ~/.hermes/memories/MEMORY.md ~/.hermes/memories/USER.md`
2. Read current content: `cat ~/.hermes/memories/MEMORY.md`
3. Identify entries to remove: resolved issues > 90 days old, stale tool versions, duplicates with USER.md
4. Write compacted version to /tmp/compacted-memory.md (DO NOT use write_file on ~/.hermes/ paths — overlay issue)
5. Apply via terminal: `cp /tmp/compacted-memory.md ~/.hermes/memories/MEMORY.md`
6. Verify all critical facts preserved
7. Run bridge: `bash scripts/memory/pre-bridge-quality.sh --fix`

### Critical Facts That Must Always Be Preserved

- /mnt/local-analysis/workspace-hub is the real mount
- ~/workspace-hub is sparse overlay — write to /tmp/ then move
- uv run on Linux, python on Windows
- digitalmodel/ is separate git repo — cd in before commits
- .legal-deny-list.yaml mandatory for doc-intelligence work
- aceengineer-strategy/ GTM context
- Hermes: 691 skills, 5 external_dirs repos
- User preferences: context parity, adversarial review, overnight batch execution

## Gateway Stability (2026-04-05 findings)

The gateway DOES stay alive with zero messaging platforms — it logs "No messaging platforms enabled" then "Gateway will continue running for cron job execution" and starts the cron ticker. The real crashes are from:

1. **API credit exhaustion** — if a cron job (e.g. gemini-overnight-batch-1) hits a 402 OpenRouter error, the gateway exits. Check `~/.hermes/logs/gateway.log` for "Non-retryable client error: Error code: 402"
2. **Restart loop** — after crash, systemd restarts it. If it again finds no platforms AND no pending cron jobs, it may exit quickly (53ms). Restart with: `systemctl restart hermes-gateway.service`
3. **Replace flag** — if gateway won't start because old PID lingers: `hermes gateway run --replace`

### Cron without gateway (manual fallback)

If gateway won't stay up, fire due jobs manually:
```
hermes cron tick
```
This ticks once and exits — no persistent gateway needed.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Gateway down | `systemctl start hermes-gateway.service`; if crashes again, check gateway.log for 402 errors |
| Bridge didn't commit (dirty submodule) | `git stash && cd /path/to/repo && bash scripts/memory/bridge-hermes-claude.sh --commit && git push` |
| Memory at 98%+ | Compact manually (steps above), then pre-bridge-quality.sh --fix |
| Windows missing context | `bash scripts/memory/bootstrap-machine.sh && git pull` |
| Drift detected | `bash scripts/memory/bridge-hermes-claude.sh --commit && git push` |
| Cron jobs not firing | Check gateway.log; if 402, pause offending job; if no platforms, gateway still works |

## Pitfalls

1. write_file/patch to ~/.hermes/ paths may hit overlay issues — use terminal to cp/mv
2. Bridge git pull --rebase fails with dirty submodules — script handles via stash/restore, but heavyequipemnt-rag may still cause issues
3. Gateway crashes — check `journalctl -u hermes-gateway --no-pager -n 30` and `~/.hermes/logs/gateway.log`
4. Existing compact-memory.py and curate-memory.py have bugs (wrong default paths) — use manual compaction instead
5. Cron output file may not exist after gateway restart
6. `hermes cron tick` works as manual fallback when gateway won't stay alive
