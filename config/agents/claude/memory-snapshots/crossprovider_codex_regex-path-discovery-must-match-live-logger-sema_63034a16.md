---
name: crossprovider codex regex-path-discovery-must-match-live-logger-sema
description: Regex path discovery must match live logger semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [path-discovery, regex, data-loss, logging]
---

A two-segment regex `([^/]+/[^/]+)` reused against arbitrary-depth logger output (e.g., `.claude/skills/*/SKILL.md`) causes 40-50% silent data loss. Test path-discovery patterns against actual logger output before reusing them in backfill/scanner code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
