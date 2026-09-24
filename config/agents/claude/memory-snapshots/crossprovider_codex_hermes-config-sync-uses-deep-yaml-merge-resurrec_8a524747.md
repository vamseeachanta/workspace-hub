---
name: crossprovider codex hermes-config-sync-uses-deep-yaml-merge-resurrec
description: Hermes config sync uses deep YAML merge, resurrecting stale entries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hermes, config-sync, yaml-merge]
---

When Hermes syncs from the canonical template, deep merge allows old provider entries (e.g., stale Anthropic fallback) to re-persist even if the template removes them. Authoritative config sections need explicit replacement logic, not merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
