---
name: crossprovider codex yaml-deep-merge-resurrects-stale-config-keys
description: YAML deep-merge resurrects stale config keys
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [config-management, hermes, yaml-patterns, drift-prevention]
---

Hermes config.yaml deep-merge reintroduces old provider/fallback entries from local state even when the canonical template changes. Managed sections (Hermes, Codex, etc.) should be replaced entirely, not deep-merged, to prevent stale drift from surviving template updates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
