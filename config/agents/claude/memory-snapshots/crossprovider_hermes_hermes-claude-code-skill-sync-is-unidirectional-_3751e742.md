---
name: crossprovider hermes hermes-claude-code-skill-sync-is-unidirectional-
description: Hermes-Claude Code skill sync is unidirectional; symlink approach blocked by Windows git
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, claude-code, architecture, cross-platform]
---

Hermes writes skills to ~/.hermes/skills/ but Claude Code reads from .claude/skills/ in repo. Bidirectional sync is missing. Symlink approach (single source of truth in ~/.hermes/, symlink in .claude/) is ideal but git on Windows doesn't handle symlinks. Dual-write is the fallback — maintain both copies on commit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
