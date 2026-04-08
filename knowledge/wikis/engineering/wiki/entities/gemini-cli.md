---
title: "Gemini CLI"
tags: [agent, gemini, google, reviewer, third-angle]
sources:
  - ai-orchestration-memory
  - ai-agent-guidelines-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Gemini CLI

Google's AI CLI. The optional third reviewer in the workspace-hub ecosystem, triggered for architecture-heavy, research-heavy, or ambiguous work.

## Role

- **Optional third reviewer** -- used when two-provider review needs a third angle
- **Non-interactive mode**: `echo content | gemini -p "prompt" -y`
- **Research agent** -- strong at synthesis-heavy work

## Trigger Conditions for Third Review

- Architecture-heavy changes
- Research-heavy or synthesis-heavy work
- Weak local verification relative to risk
- Unresolved ambiguity after first adversarial review

## Integration

- Reads from `.claude/skills/` (shared knowledge base)
- Provider adapter: `scripts/agents/providers/gemini.sh`
- Symlink: `.gemini/skills` -> `../.claude/skills`
- Paid Google Workspace API access available for GWS integration

## Cross-References

- **Related entity**: [Claude Code](../entities/claude-code.md)
- **Related entity**: [Codex CLI](../entities/codex-cli.md)
- **Related concept**: [[three-agent-cross-review]]
- **Related concept**: [[multi-agent-parity]]
