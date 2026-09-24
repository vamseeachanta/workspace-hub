---
name: crossprovider codex claude-code-auto-loads-claude-rules-directory
description: Claude Code auto-loads .claude/rules/ directory
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure, claude-code, config]
---

.md files in .claude/rules/ are materialized into Claude Code system prompt per-message without explicit reference in CLAUDE.md. Use this surface for durable, repo-tracked operational rules rather than inline embedding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
