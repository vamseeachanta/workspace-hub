---
name: crossprovider codex provisional-contracts-in-upstream-dependencies
description: Provisional contracts in upstream dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [dependencies, contracts, fixtures]
---

Nested upstream gates may reference provisional policies (marked `provisional_fixture_contract: true`) that become stable only after upstream completion. Cannot treat provisional fixtures as final policy until the upstream issue completes and removes the provisional marker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
