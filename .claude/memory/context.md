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
- Provider-session audit transfer (2026-04-24): Hermes, Gemini, and Codex
  still show meaningful bare `python3` usage in recent corpora. Agent prompts
  and review comments should explicitly preserve the Linux `uv run ... python`
  rule when dispatching non-Claude providers.

## Workspace Layout (Linux)

- `/mnt/local-analysis/workspace-hub/` — the real git repo mount
- `~/workspace-hub` — **sparse overlay** on ace-linux-1; writes may fail silently *stale: 2026-04-17*
  - If a write via tool fails: write to `/tmp/` first, then `mv` via terminal to the real mount
- `digitalmodel/` — **separate git repo** (vamseeachanta/digitalmodel.git), gitignored by parent
- Commits MUST be made from inside `digitalmodel/` — not from workspace-hub root *verified: 2026-04-19*
- `aceengineer-strategy/` — private GTM strategy repo, nested, gitignored by parent *verified: 2026-04-17*
- `worldenergydata/` — energy data sub-repo *verified: 2026-04-19*
- Provider-session audit transfer (2026-04-24): missing reads from Codex often
  come from running at the workspace-hub root while the real target belongs to a
nested repo or site content root. Check `digitalmodel/`, `worldenergydata/`, *verified: 2026-04-24*
`assethold/`, and `aceengineer-website/` before treating those paths as *verified: 2026-04-25*
  deleted workspace-hub files.
- Hermes audit interpretation (2026-04-24): reads under `.claude/worktrees/`,
  `.worktrees/`, `/mnt/local-analysis/worktrees/`, and `/tmp/` are usually
  session-local worktree artifacts. Promote only durable outputs back to
  repo-root docs, plans, skills, or scripts.

## Windows Path Conventions

- MINGW64 bash: paths use `/d/workspace-hub/` (not `D:\workspace-hub`)
- `core.symlinks=false` — git treats junctions as dirs; never commit symlinks cross-platform
- Shell scripts: `#!/usr/bin/env bash`, LF line endings *stale: 2026-04-23*

## Memory Sync Model

Memory travels with the repo via git. No Hermes needed on Windows.

1. **Hermes (ace-linux-1)**: Writes authoritative facts to `~/.hermes/memories/`
2. **Bridge script** (`scripts/memory/bridge-hermes-claude.sh`): Reads Hermes memory, *verified: 2026-04-12*
injects it into the `<!-- BRIDGE:START/END -->` section of `agents.md` via template, *stale: 2026-04-17*
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
