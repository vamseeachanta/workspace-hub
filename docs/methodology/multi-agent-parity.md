# Multi-Agent Parity

> All agents should have equal knowledge without redundant discovery

## The Problem

When you use multiple AI agents (Hermes, Claude Code, Codex, Gemini), each one discovers things independently. Claude Code might learn that a certain file structure is needed. Codex might figure out an encoding trick. Hermes might develop a workflow. None of this knowledge automatically transfers to the others.

### Why This Is Expensive

- Setting up a fresh agent takes hours of "discovery" that others already completed
- The same questions get answered multiple times across agents
- Skills created for one agent don't benefit others
- User corrections to one agent aren't seen by others

```
Agent A spends 2 hours figuring out Python encoding issues -> solves it
Agent B spends 2 hours figuring out the SAME encoding issues -> solves it again
Agent C never encountered it -> will spend 2 hours next time
```

## The Solution

**Shared knowledge base via repository-tracked files.**

### Architecture

```
workspace-hub/.claude/           (git repository)
├── skills/                      (all skills, all agents read)
│   ├── orcaflex/                (engineering)
│   ├── ffd/                     (fitness-for-service)
│   └── ...
├── commands/                    (slash commands)
├── AGENTS.md                    (agent conventions)
├── CLAUDE.md                    (Claude-specific context)
└── hooks/                       (enforcement)

All agents read from → SAME DIRECTORY
```

### How Each Agent Accesses Shared Knowledge

| Agent | Read Path | Write Path | Sync Mechanism |
|-------|-----------|-----------|----------------|
| Claude Code | .claude/skills/ | .claude/skills/ | Git commit on every change |
| Codex | .claude/skills/ | .claude/skills/ | Git commit on every change |
| Gemini | .claude/skills/ | .claude/skills/ | Git commit on every change |
| Hermes | symlink -> .claude/skills/ | .claude/skills/ (via symlink) | Git commit on every change |

### The Secret Sauce

What makes this work in practice:

1. **Everything is git-committed immediately** -- no untracked knowledge
2. **Skills are the primary carrier** -- not session memory
3. **WRITE-BACK RULE** -- new skills go to `.claude/skills/` not `~/.hermes/skills/`
4. **Symlinks for agents with different base paths** -- Hermes reads from repo via symlink
5. **No agent silos** -- if one agent learns it, all can learn

## Context Parity Mandate

User directive: "corrections in one agent sync to ALL others."

### How Parity Works

```
User corrects Claude: "Always use uv run, not python3"
    │
    └─> Claude updates .claude/AGENTS.md or creates a skill
         │
         └─> Git commits the change
              │
              └─> Codex sees updated file on next session
                   │
                   └─> Gemini sees it too
                        │
                        └─> Hermes sees it too (via symlink)
```

### What Breaks Parity

| Anti-pattern | Problem | Fix |
|---|---|---|
| Agent stores info in session memory | Lost when session ends | Must be written to file |
| Knowledge stored in `~/.hermes/memory/` | Only Hermes can read it | Mirror to repo |
| Agent memory stores facts | Other agents don't have access | Use repo files for shared memory |
| Skills only in `~/.hermes/skills/` | Only Hermes sees them | Must be in `.claude/skills/` |

## Implementation Reference

### File Locations
- `.claude/skills/` -- Single source of truth for all agent skills
- `.claude/AGENTS.md` -- Agent conventions (all agents read this)
- `.claude/CLAUDE.md` -- Claude-specific context (Claude reads this)
- `docs/modules/ai/` -- Architecture documentation
- `scripts/learnings/cross-agent-bridge.sh` -- Automated sync tool (#1760 Phase 5)

### Memory Bridge

The `cross-agent-bridge.sh` script provides automated syncing:

```bash
# Bridge local agent memory to repo-tracked files
bash scripts/learnings/cross-agent-bridge.sh bridge

# Check bridge status
bash scripts/learnings/cross-agent-bridge.sh status
```

### The Parity Checklist

- [ ] All agents read from `.claude/skills/`
- [ ] No agent stores critical knowledge outside the repo
- [ ] New skills go to `.claude/skills/` immediately
- [ ] User corrections trigger file updates, not just session memory
- [ ] Cross-agent bridge runs on a schedule (nightly cron)
- [ ] Bypass logging tracks any knowledge that stays local

## Related

- #1760 (self-improvement commands -- Phase 5: cross-agent bridge)
- #112 (cowork relevance + multi-agent ecosystem fit)
- docs/methodology/compound-engineering.md (Lesson 4: Multi-Agent Parity)
- WRITE-BACK RULE -- memory system entry
- agent-memory-bridge skill -- bidirectional sync
