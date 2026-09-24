---
name: crossprovider codex bootstrap-baseline-paths-must-be-canonicalized-a
description: Bootstrap/baseline paths must be canonicalized across sources
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bootstrap, configuration, validation]
---

When multiple docs/scripts define initialization paths (e.g., /usr/lib vs /opt), plans must freeze ONE canonical path and verify it matches live implementation. Path disagreement becomes a blocking issue during execution if not resolved pre-implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
