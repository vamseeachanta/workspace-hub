---
name: crossprovider codex latent-contract-mismatches-between-strict-and-le
description: Latent contract mismatches between strict and legacy code paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, contracts, testing, legacy-code]
---

Legacy coverage counters can diverge from canonical contract specs without breaking strict validation paths. The `doc_key` validator counts any `doc_key:` line as covered, but the plan specifies only canonical `sha256:<64 hex>` should count; strict changed-path mode catches this at the gate, but latent reporting-accuracy debt persists in legacy aggregate counters. Test edge cases separately for both paths; do not assume strict-path validation covers legacy-path accuracy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
