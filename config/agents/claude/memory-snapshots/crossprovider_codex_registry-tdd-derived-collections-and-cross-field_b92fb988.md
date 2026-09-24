---
name: crossprovider codex registry-tdd-derived-collections-and-cross-field
description: Registry TDD: Derived Collections and Cross-Field Invariants
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, registry, configuration, derived-data]
---

Configuration registry tests should verify that computed/derived collections resolve correctly (e.g., repo paths under declared `tier1_repo_root`), not just that fields exist. Test cross-field invariants (e.g., `tier1_repo_root != workspace_root`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
