---
name: crossprovider codex array-merge-semantics-in-config-apply-are-a-bloc
description: Array merge semantics in config apply are a blocker if undefined
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [config-management, live-safety, arrays]
---

Config changes (hooks, deny lists) involving arrays need explicit merge behavior: union, replace, append, or keyed identity. Undefined semantics can cause silent duplicates, deleted safety rules, or silent conflicts when applied, especially in live environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
