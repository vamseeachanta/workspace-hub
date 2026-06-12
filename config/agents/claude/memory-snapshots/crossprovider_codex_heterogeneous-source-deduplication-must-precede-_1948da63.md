---
name: crossprovider codex heterogeneous-source-deduplication-must-precede-
description: Heterogeneous source deduplication must precede pseudocode
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-integration, schema-design, deduplication]
---

Plans combining multiple source surfaces (registries, ledgers, inventories) fail when dedup logic is undefined: does canonical key from N sources count as 1 record or N? Field precedence and coverage accounting flow from this choice. Specify dedup strategy and field mapping per source type before implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
