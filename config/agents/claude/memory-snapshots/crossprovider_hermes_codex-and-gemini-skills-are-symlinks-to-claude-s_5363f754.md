---
name: crossprovider hermes codex-and-gemini-skills-are-symlinks-to-claude-s
description: .codex and .gemini skills are symlinks to .claude/skills
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-agent-skills, architecture, skill-ecosystem]
---

Cross-agent skill ecosystem changes under `.claude/skills/` affect all three agents (Claude/Codex/Gemini) immediately via symlinks. Avoid per-provider skill maintenance; consolidate at `.claude/` level. Context-efficient skill patterns (isolated workers, file-backed handoffs, compact status) improve all three providers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
