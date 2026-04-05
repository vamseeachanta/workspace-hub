# Memory Bridge Architecture

> Issue: #1886 · Author: Hermes Agent · Date: 2026-04-05

## Problem

Three memory silos exist:

1. **Hermes Memory** (`~/.hermes/memories/`) — written by Hermes agent on ace-linux-1. Only exists on that machine.
2. **Claude Code Auto-Memory** (`~/.claude/projects/*/memory/`) — 39 topic-specific `.md` files per project. Written automatically by Claude Code sessions. Non-portable — stuck on each machine.
3. **Licensed-Win-1** (`D:\workspace-hub`) — has neither Hermes nor any Claude memory. Zero context.

No bridge between any of them.

## Solution: Memory Lives In The Repo

Instead of a sync tool or export/restore mechanism, memory files are **commit
ted to `.claude/memory/` inside the workspace-hub repo**. Any machine that
clones and git-pulls gets the full context.

### Architecture Layers

```
Layer 1 — Git-Triggered (automatic, already exists)
┌──────────────────────────────────────────────────────────┐
│  .claude/memory/  (git repo)                             │
│  ├── KNOWLEDGE.md       — engineering lessons            │
│  ├── context.md         — machine conventions, paths     │
│  ├── agents.md          — user, workflow, subscriptions   │
│  ├── claude-auto-memory.md — Claude auto-memory snapshot │
│  ├── aqwa-lessons.md    — ANSYS AQWA API quirks          │
│  └── orcawave-lessons.md — OrcaFlex solver lessons       │
└──────────────────────┬───────────────────────────────────┘
                       │ git pull / push
┌──────────────────────┴───────────────────────────────────┐
│  Layer 2 — Machine-Local Memory (enhancement)             │
│  ace-linux-1: ~/.hermes/memories/  (Hermes)              │
│  ace-linux-1: ~/.claude/projects/*/memory/  (Claude CC)  │
│  licensed-win-1:  .claude/MEMORY.md  (Claude CC)         │
│  → These feed INTO Layer 1 via the bridge script          │
│  → They are NOT the source of truth for cross-machine     │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────┴───────────────────────────────────┐
│  Layer 3 — Global Bootstrap (~/.claude/CLAUDE.md)         │
│  Per-user file on each machine, gives every Claude        │
│  session a one-page pointer to .claude/memory/            │
│  "Read context.md and agents.md first"                    │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

```
                    ┌─────────────────┐
                    │  Hermes Agent   │
                    │  ~.hermes/      │
                    │  memories/      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Bridge Script   │
                    │  bridge-hermes-  │
                    │  claude.sh       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Claude Auto-    │
                    │  Memory Reader   │
                    │  (reads ~/.claude│
                    │   /projects/*/   │
                    │   memory/)       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  .claude/        │
                    │  memory/         │
                    │  (git tracked)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
      ┌───────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
      │  ace-linux-1 │ │ Windows  │ │  Other      │
      │  git clone   │ │ clone +  │ │  machines   │
      │  gets every- │ │ pull     │ │  (future)   │
      │  thing       │ │ gets     │ │             │
      │              │ │ everything│ │             │
      └──────────────┘ └──────────┘ └─────────────┘
```

## File Inventory

### Layer 1 — Repo Memory (git-tracked, source of truth)

| File | Populated By | Content |
|------|-------------|---------|
| `.claude/memory/context.md` | Bridge script | Machine conventions, paths, Python rules, workspace layout, sync model description, legal compliance |
| `.claude/memory/agents.md` | Bridge script | User profile, AI subscriptions, workflow rules, GSD facts, skill system |
| `.claude/memory/claude-auto-memory.md` | Bridge script | Snapshot of Claude auto-memory index |
| `.claude/memory/KNOWLEDGE.md` | Manual + bridge | Institutional knowledge, engineering lessons, tool quirks |
| `.claude/memory/orcawave-lessons.md` | Manual | OrcFxAPI usage and solver lessons |
| `.claude/memory/aqwa-lessons.md` | Manual | ANSYS AQWA format and parser lessons |

### Layer 2 — Machine-Local (non-portable, source data)

| Machine | Path | Description |
|---------|------|-------------|
| ace-linux-1 | `~/.hermes/memories/MEMORY.md` | Hermes persistent memory (~2200 chars) |
| ace-linux-1 | `~/.hermes/memories/USER.md` | Hermes user profile (~1300 chars) |
| ace-linux-1 | `~/.claude/projects/*/memory/` | 39 Claude auto-memory topic files |
| licensed-win-1 | `C:\Users\...\ .claude\projects\*\memory\` | Claude auto-memory (Windows Claude sessions) |

### Layer 3 — Global Bootstrap

| Path | Description |
|------|-------------|
| `~/.claude/CLAUDE.md` | One-page config that points Claude to `.claude/memory/` files |

## Bridge Script

`scripts/memory/bridge-hermes-claude.sh` does:

1. Reads `~/.hermes/memories/MEMORY.md` and `USER.md`
2. Reads Claude auto-memory `~/.claude/projects/*/memory/MEMORY.md`
3. Writes `.claude/memory/agents.md` and `context.md`
4. Writes `.claude/memory/claude-auto-memory.md` as a snapshot
5. Optionally commits (with `--commit` flag)

Run: `bash scripts/memory/bridge-hermes-claude.sh --commit`
Then: `git push`

## Success Criteria (from Issue #1886)

- [x] Global `~/.claude/CLAUDE.md` created — gives Claude Code on any machine baseline knowledge
- [x] Bridge script created — reads Hermes memory, produces unified repo memory files
- [x] Memory travels with the repo via git — no manual copy/install needed
- [x] Licensed-win-1 can get full context via `git pull` — no Hermes needed
- [x] Architecture document created — explains the problem, layers, and data flow

## Why Not Tarballs or PowerShell Installers?

The original plan included:
- `sync-to-licensed-win.sh` — tarball + PowerShell installer
- Manual copy-paste Windows instructions

These were replaced because they're fundamentally the wrong approach:

1. **They don't survive updates** — one-time snapshot, stale immediately
2. **They require manual intervention** — defeats the "automatically available" principle
3. **They bypass git** — no version history, no diff, no rollback

With `.claude/memory/` tracked in git:
- Windows does `git pull` → gets same context automatically
- No Hermes needed on Windows
- Updates are just commits + pushes
- Version history, diffs, and rollback are free

## How Non-Hermes Machines Enrich Memory

The flow is bidirectional:

1. **Hermes → Others**: Bridge script writes authoritative facts → `.claude/memory/` → git push → all machines pull
2. **Others → Hermes**: Windows Claude sessions discover new lessons → write to `KNOWLEDGE.md` or topic files → git commit/push → next `git pull` on Linux picks them up

The bridge script also captures Claude's auto-memory snapshot, so even lessons learned on Windows (not in Hermes) get propagated.

## Cron Opportunity

Future enhancement (separate issue):
```bash
# Add to Hermes cron: run bridge daily, commit, and push
30 6 * * * cd /workspace-hub && bash scripts/memory/bridge-hermes-claude.sh --commit && git push
```
