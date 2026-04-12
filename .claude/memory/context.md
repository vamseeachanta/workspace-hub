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
- `aceengineer-strategy/` — private GTM strategy repo, nested, gitignored by parent
- `worldenergydata/` — energy data sub-repo

## Windows Path Conventions

- MINGW64 bash: paths use `/d/workspace-hub/` (not `D:\workspace-hub`)
- `core.symlinks=false` — git treats junctions as dirs; never commit symlinks cross-platform
- Shell scripts: `#!/usr/bin/env bash`, LF line endings

## Memory Sync Model

Memory travels with the repo via git. No Hermes needed on Windows.

1. **Hermes (ace-linux-1)**: Writes authoritative facts to `~/.hermes/memories/`
2. **Bridge script** (`scripts/memory/bridge-hermes-claude.sh`): Reads Hermes memory, *verified: 2026-04-12*
   injects it into the `<!-- BRIDGE:START/END -->` section of `agents.md` via template,
   mirrors Claude auto-memory topic files to `topics/`, commits and pushes.
3. **Windows (licensed-win-1)**: `git pull` — gets updated `.claude/memory/` automatically. *verified: 2026-04-11*
4. **Return enrichment**: New lessons learned on any machine go into `KNOWLEDGE.md`
   or topic files, committed and pushed. Next `git pull` on any machine picks them up.

Git IS the sync mechanism.

## Legal Compliance

- `.legal-deny-list.yaml` — 15 client name patterns, repo root
- Run `scripts/legal/legal-sanity-scan.sh` before committing any generated documents
- Catalogs (`dde-*`, `conference-*`) are excluded from scanning
- MANDATORY for all document-intelligence and resource work
