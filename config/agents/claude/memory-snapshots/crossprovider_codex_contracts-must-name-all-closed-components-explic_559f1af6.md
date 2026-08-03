---
name: crossprovider codex contracts-must-name-all-closed-components-explic
description: Contracts must name all closed components explicitly, not just forbid some fields
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [architecture, contracts, validation]
---

The run-dataset contract learned that forbidding certain fields (run_id, private/attempt) is insufficient. Must define the positive set of components for record identity and ownership, then test exact one-to-one mappings including residency tables and decision briefs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
