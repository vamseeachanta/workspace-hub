---
name: crossprovider codex policy-schema-backward-compatibility-with-append
description: Policy schema backward compatibility with append_only contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-versioning, backward-compatibility, data-contracts]
---

When upgrading from v1 to v2 of a policy schema, declare `append_only_v1: true` in the new schema and configure the loader to accept previous-version artifacts with matching audit_scope. This prevents baseline discontinuity across version upgrades. Add regression tests (e.g., `test_v2_first_run_after_v1_baseline_carries_forward_legacy_findings`) to verify carry-forward works.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
