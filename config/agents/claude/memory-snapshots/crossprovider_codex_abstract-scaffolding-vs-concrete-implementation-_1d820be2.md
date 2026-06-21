---
name: crossprovider codex abstract-scaffolding-vs-concrete-implementation-
description: Abstract scaffolding vs concrete implementation — watch for AC ambiguity when spec calls for both
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [specification, scaffolding-vs-implementation, acceptance-criteria]
---

A queue that emits abstract route-classes (taxonomy) is not a per-item queue (execution). The acceptance criterion 'every item has a route target before ingestion' may require both: abstract routing rules AND concrete item assignment. Pre-implementation, clarify whether AC is satisfied by abstract taxonomy or needs concrete source/item coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
