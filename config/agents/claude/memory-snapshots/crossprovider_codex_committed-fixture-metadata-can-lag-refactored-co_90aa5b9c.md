---
name: crossprovider codex committed-fixture-metadata-can-lag-refactored-co
description: Committed fixture metadata can lag refactored code
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [metadata-staleness, fail-closed-contracts, cross-file-consistency, data-refactors]
---

When accepting new data factors or changing data transformations, verify committed artifact metadata (_metadata.json, fixture provenance) reflects the new citations and factors, not just test assertions. Stale fixture metadata violates fail-closed contracts and creates cross-file consistency gaps that tests in the changed files won't catch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
