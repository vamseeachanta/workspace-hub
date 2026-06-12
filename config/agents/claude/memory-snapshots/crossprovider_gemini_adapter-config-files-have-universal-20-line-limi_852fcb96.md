---
name: crossprovider gemini adapter-config-files-have-universal-20-line-limi
description: Adapter config files have universal ≤20-line limit
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [config-standards, line-limits, cross-review-gates]
---

All adapter configuration files (CLAUDE.md, AGENTS.md, GEMINI.md, CODEX.md, MEMORY.md) must be ≤20 lines per `.claude/rules/coding-style.md`. This is a hard constraint across all workspace-hub tiers. Route B work requires cross-review before merge, which gates on this limit.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
