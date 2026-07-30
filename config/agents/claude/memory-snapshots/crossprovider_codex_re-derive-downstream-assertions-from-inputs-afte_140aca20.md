---
name: crossprovider codex re-derive-downstream-assertions-from-inputs-afte
description: Re-derive downstream assertions from inputs after algorithm changes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [testing, algorithm-changes, correctness, assertions]
---

When algorithm changes affect production outputs, recompute dependent assertions from inputs rather than updating them to match new values; this catches subtle correctness issues that value-only updates would miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
