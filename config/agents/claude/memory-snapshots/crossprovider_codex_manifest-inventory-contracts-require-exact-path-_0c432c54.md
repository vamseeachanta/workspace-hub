---
name: crossprovider codex manifest-inventory-contracts-require-exact-path-
description: Manifest/inventory contracts require exact path enumeration and bidirectional verification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [data-integrity, verification, configuration]
---

If a manifest lists 'five connection wrappers' but the actual paths don't match by name, all validation becomes impossible. Fix: enumerate paths exactly, verify each exists in repo, and compare the populated manifest against the actual file list as a blocking gate. Inventory count mismatches (claimed 19, actual 20) are Critical findings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
