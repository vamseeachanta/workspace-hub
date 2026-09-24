---
name: crossprovider codex optional-consumer-hooks-without-breaking-existin
description: Optional consumer hooks without breaking existing contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [backward-compatibility, contracts, api-design]
---

When adding new consumption paths for derived data, use optional parameters and lazy exports that default to current behavior. Prevents cascading refactors across existing downstream code and allows incremental adoption of new data sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
