# Cross-Machine Context

> Git-tracked. Travels with the repo. Managed by scripts/memory/bridge-hermes-claude.sh
> Source of truth for environment conventions on every machine that clones workspace-hub.

## Machines

| Machine | OS | Hermes | Python cmd | Workspace root |
|---------|----|--------|------------|----------------|
| ace-linux-1 | Linux | YES | `uv run` | `/mnt/local-analysis/workspace-hub` |
| licensed-win-1 | Windows | NO | `python` | `D:\workspace-hub` |

## Python Command Rule

- **Linux**: ALWAYS `uv run` — never bare `python3` or `pip`
- **Windows**: Use `python` — uv is NOT installed on licensed-win-1

## Workspace Layout (Linux)

- `/mnt/local-analysis/workspace-hub/` — the real git repo mount
- `~/workspace-hub` — **sparse overlay** on ace-linux-1; writes may fail silently
  - If a write via tool fails: write to `/tmp/` first, then `mv` via terminal to the real mount
- `digitalmodel/` — **separate git repo** (vamseeachanta/digitalmodel.git), gitignored by parent
  - Commits MUST be made from inside `digitalmodel/` — not from workspace-hub root
- `aceengineer-strategy/` — private GTM strategy repo, nested, gitignored by parent *verified: 2026-05-05*
- `worldenergydata/` — energy data sub-repo *verified: 2026-05-05*

## Windows Path Conventions

- MINGW64 bash: paths use `/d/workspace-hub/` (not `D:\workspace-hub`)
- `core.symlinks=false` — git treats junctions as dirs; never commit symlinks cross-platform
- Shell scripts: `#!/usr/bin/env bash`, LF line endings

## Memory Sync Model

Memory travels with the repo via git. No Hermes needed on Windows.

1. **Hermes (ace-linux-1)**: Writes authoritative facts to `~/.hermes/memories/`
2. **Bridge script** (`scripts/memory/bridge-hermes-claude.sh`): Reads Hermes memory *verified: 2026-05-03*
   (if present), injects it into `agents.md` via template, regenerates `context.md`,
   snapshots Claude auto-memory, mirrors topic files, commits and pushes.
   Runs on both Linux (cron) and Windows (Task Scheduler).
3. **Windows (licensed-win-1)**: Runs the same bridge script via Task Scheduler.
   Hermes steps are skipped (no Hermes on Windows); context.md, auto-memory
   snapshot, and topic mirrors are refreshed and pushed back to repo.
4. **Return enrichment**: New lessons learned on any machine go into `KNOWLEDGE.md`
   or topic files, committed and pushed. Next `git pull` on any machine picks them up.

Git IS the sync mechanism.

## Legal Compliance

- `.legal-deny-list.yaml` — 15 client name patterns, repo root
- Run `scripts/legal/legal-sanity-scan.sh` before committing any generated documents *verified: 2026-05-07*
- Catalogs (`dde-*`, `conference-*`) are excluded from scanning
- MANDATORY for all document-intelligence and resource work
