---
name: crossprovider codex cross-cutting-governance-via-hooks-without-agent
description: Cross-cutting governance via hooks without agent code changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hooks, governance, configuration, separation-of-concerns]
---

Use PreToolUse/PostToolUse hooks in settings.json to inject session logging, readiness checks, and signal emission. Decouples audit/governance from agent logic, allows centralized updates without agent binary changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
