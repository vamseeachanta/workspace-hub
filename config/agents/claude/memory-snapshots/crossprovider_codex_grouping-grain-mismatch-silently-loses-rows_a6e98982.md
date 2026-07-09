---
name: crossprovider codex grouping-grain-mismatch-silently-loses-rows
description: Grouping grain mismatch silently loses rows
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [data-correctness, testing, aggregation]
---

Aggregating on one grain (API10) while the spec expects another (API14) produces one output per API10, silently dropping duplicate sources. Grain-level tests must verify deduplication behavior at the expected cardinality.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
