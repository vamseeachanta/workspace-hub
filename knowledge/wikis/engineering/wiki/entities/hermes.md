---
title: "Hermes"
tags: [agent, hermes, multi-agent, orchestration]
sources:
  - ai-orchestration-memory
added: 2026-04-08
last_updated: 2026-04-08
---

# Hermes

Multi-agent orchestration framework (v0.4.0). Connects to multiple AI providers and delegates tasks between them.

## Key Features

- Provider routing via `config.yaml`
- `delegate_task` for spawning focused sub-agents
- Skill symlinks to `.claude/skills/` for shared knowledge
- Shebang reverts recurring (known issue, fixed 3x)

## Integration

- Symlink: reads from repo `.claude/skills/` directory
- Skills are the primary knowledge carrier across agents
- Write-back rule: new skills go to `.claude/skills/`, not `~/.hermes/skills/`

## Known Issues

- Shebang reverts recurring (3x fixed)
- `config.yaml` provider routing needed manual fix

## Cross-References

- **Related entity**: [Claude Code](../entities/claude-code.md)
- **Related entity**: [Skills System](../entities/skills-system.md)
- **Related concept**: [[multi-agent-parity]]
- **Related concept**: [[orchestrator-worker-separation]]
