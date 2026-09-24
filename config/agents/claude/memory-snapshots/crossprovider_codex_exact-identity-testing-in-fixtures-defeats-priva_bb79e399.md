---
name: crossprovider codex exact-identity-testing-in-fixtures-defeats-priva
description: Exact-identity testing in fixtures defeats privacy containment
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, testing, implementation-hazard, batch-systems]
---

When tests validate against sensitive identities (source labels, paths, codes) and store those identities in tracked test fixtures or config files, you create a persistent source map that defeats containment claims. Either use in-memory-only validation or accept the source data is now leaked to the code repo.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
