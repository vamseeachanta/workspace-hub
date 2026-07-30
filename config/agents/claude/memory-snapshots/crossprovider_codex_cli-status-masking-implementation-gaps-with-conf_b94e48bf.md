---
name: crossprovider codex cli-status-masking-implementation-gaps-with-conf
description: CLI status masking implementation gaps with config names
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [cli-design, testing]
---

A provider status command listing configured names or hardcoded provider identifiers (instead of checking actual implementation and reachability) will claim availability for missing or incomplete providers, deferring discovery until runtime.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
