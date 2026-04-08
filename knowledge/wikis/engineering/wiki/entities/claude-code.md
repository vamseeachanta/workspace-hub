---
title: "Claude Code"
tags: [agent, claude, orchestrator, anthropic, cli]
sources:
  - ai-orchestration-memory
  - ai-agent-guidelines-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Claude Code

Anthropic's CLI for Claude. The default orchestrator in the workspace-hub ecosystem. All sessions start with Claude Code as the primary work surface.

## Role

- **Default orchestrator** -- coordinates all work
- **Primary implementer** -- writes code, creates files, runs tests
- **Subagent spawner** -- delegates focused tasks to workers
- **Review coordinator** -- routes reviews to Codex/Gemini

## Models

| Model | Cost (in/out per M) | Use Case |
|-------|---------------------|----------|
| Opus 4.6 | $5/$25 | Complex architecture, 1M-context |
| Sonnet 4.6 | $3/$15 | Default for most work |

## Key Configuration

- `CLAUDE.md` -- project-level instructions
- `AGENTS.md` -- cross-agent conventions
- `.claude/skills/` -- shared skill definitions
- `.claude/hooks/` -- enforcement hooks
- `.claude/memory/` -- session memory

## Working Model

Single terminal model -- Claude Code is the primary work surface. Agentic code made multi-terminal tab-switching obsolete.

## Cross-References

- **Related entity**: [Codex CLI](../entities/codex-cli.md)
- **Related entity**: [Gemini CLI](../entities/gemini-cli.md)
- **Related entity**: [Hermes](../entities/hermes.md)
- **Related concept**: [[orchestrator-worker-separation]]
- **Related concept**: [[agent-delegation]]
