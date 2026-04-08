---
title: "Multi-Agent Parity"
tags: [methodology, parity, agents, knowledge-sharing, sync]
sources:
  - compound-engineering-methodology
  - ai-orchestration-memory
added: 2026-04-08
last_updated: 2026-04-08
---

# Multi-Agent Parity

All agents should have equal knowledge without redundant discovery. When Claude, Codex, Gemini, and Hermes each discover things independently, the same questions get answered multiple times.

## The Problem

```
Agent A spends 2 hours figuring out Python encoding issues -> solves it
Agent B spends 2 hours figuring out the SAME encoding issues -> solves it again
Agent C never encountered it -> will spend 2 hours next time
```

## The Solution

**Shared knowledge base via repository-tracked files.**

| Agent | Read Path | Sync Mechanism |
|-------|-----------|----------------|
| Claude Code | .claude/skills/ | Git commit on every change |
| Codex | .claude/skills/ | Git commit on every change |
| Gemini | .claude/skills/ | Git commit on every change |
| Hermes | symlink -> .claude/skills/ | Git commit on every change |

## The Secret Sauce

1. **Everything is git-committed immediately** -- no untracked knowledge
2. **Skills are the primary carrier** -- not session memory
3. **WRITE-BACK RULE** -- new skills go to `.claude/skills/` not agent-local paths
4. **Symlinks for agents with different base paths**
5. **No agent silos** -- if one agent learns it, all can learn

## Context Parity Mandate

Corrections in one agent sync to ALL others via the git-tracked shared directory.

## Cross-References

- **Source**: [Compound Engineering Methodology](../sources/compound-engineering-methodology.md)
- **Related concept**: [[compound-engineering]]
- **Related concept**: [[orchestrator-worker-separation]]
- **Related entity**: [Skills System](../entities/skills-system.md)
