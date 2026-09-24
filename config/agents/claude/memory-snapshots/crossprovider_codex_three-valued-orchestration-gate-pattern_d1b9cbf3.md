---
name: crossprovider codex three-valued-orchestration-gate-pattern
description: Three-valued orchestration gate pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [orchestration, gates, typing-patterns]
---

Use `tuple[bool | None, str]` returns for gates: True = pass, False = fail (hard error), None = warn-only (legacy item, non-critical). Allows gates to distinguish soft warnings from blocking failures without separate exception types or enum variants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
