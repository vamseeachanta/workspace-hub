---
title: "Codex CLI"
tags: [agent, codex, openai, reviewer, adversarial]
sources:
  - ai-orchestration-memory
  - ai-agent-guidelines-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Codex CLI

OpenAI's coding agent CLI. The default adversarial reviewer in the workspace-hub ecosystem.

## Role

- **Default adversarial reviewer** -- reviews Claude's implementation diffs, tests, and artifacts
- **Implementation agent** -- user preference to use Codex for coding too, not just review
- **Bounded work** -- implementation, test writing, review, refactoring

## Availability

- NOT on dev-primary (ace-linux-1)
- Run via SSH to ace-linux-2
- When Codex quota is exhausted, substitute Claude Opus as cross-reviewer

## Integration

- Reads from `.claude/skills/` (shared knowledge base)
- Provider adapter: `scripts/agents/providers/codex.sh`
- Symlink: `.codex/skills` -> `../.claude/skills`

## Cross-References

- **Related entity**: [Claude Code](../entities/claude-code.md)
- **Related entity**: [Gemini CLI](../entities/gemini-cli.md)
- **Related concept**: [[three-agent-cross-review]]
- **Related concept**: [[multi-agent-parity]]
