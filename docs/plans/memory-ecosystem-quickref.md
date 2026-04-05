# Memory Ecosystem Quick Reference

> One-screen guide to the memory sync system. Created: 2026-04-05.

## Architecture

```
Hermes Agent (ace-linux-1)
  writes → ~/.hermes/memories/ (MEMORY.md + USER.md, ~2200 chars)
    ↓
Bridge Script (daily 04:00 cron)
  reads Hermes memory → injects into template → .claude/memory/
    ↓
Git (the sync mechanism)
  push → every machine sees the same context via git pull
    ↓
Windows, other machines, new clones
  git pull → full context, no manual setup needed
```

## Script Inventory

| Script | What | When |
|--------|------|------|
| `scripts/memory/bridge-hermes-claude.sh --commit` | Syncs Hermes memory → .claude/memory/ → git commit + push | Daily cron (04:00) |
| `scripts/memory/pre-bridge-quality.sh --fix` | Quality gate + compacts memory before bridge | Used by cron |
| `scripts/memory/check-memory-drift.sh` | Warns when Hermes memory ahead of repo | On-demand |
| `scripts/memory/bootstrap-machine.sh` | Sets up ~/.claude/CLAUDE.md on new machine | Once per machine |
| `scripts/upkeep/health-check.sh --save` | 16-check health report (gateway, cron, memory, disk, repos) | Manual + future cron |
| `scripts/memory/compact-memory.py` | Compacts memory to fit within char limits | Manual (#1915) |
| `scripts/memory/curate-memory.py` | Removes stale entries, reorganizes | Manual (#1915) |

## Quick Troubleshooting

```bash
# Everything broken? Run health check first
bash scripts/upkeep/health-check.sh

# Gateway dead (cron won't fire)?
sudo systemctl start hermes-gateway.service

# Memory at 98%, bridge might push bad data?
bash scripts/memory/pre-bridge-quality.sh --fix

# Bridge didn't run, memory stale?
bash scripts/memory/bridge-hermes-claude.sh --commit && git push

# Windows machine has no context?
bash scripts/memory/bootstrap-machine.sh
git pull

# Something broke, need a clean state?
bash scripts/memory/check-memory-drift.sh  # see what's missing
```

## Cron Schedule

| Job | Schedule | What |
|-----|----------|------|
| memory-bridge-daily | 04:00 daily | Quality gate → bridge → commit/push |
| deepseek-weekly-check | Mon 09:00 | (separate check) |

## Key Directories

| Path | Purpose |
|------|---------|
| `~/.hermes/memories/` | Hermes memory (MEMORY.md + USER.md) — source of truth |
| `.claude/memory/` | Git-tracked repo memory — what all machines read |
| `.claude/memory/topics/` | Mirrored Claude auto-memory feedback files |
| `.claude/memory/templates/` | agents-template.md — baseline content for bridge injection |
| `logs/upkeep/` | Daily health reports |
