---
name: crossprovider codex stale-test-assertions-acceptable-if-unused-by-pr
description: Stale test assertions acceptable if unused by production call sites
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-maintenance, code-churn, legacy-paths]
---

A test asserting legacy behavior (e.g., a defaulted-field path no longer invoked by production code) can remain without modification to avoid churn. Requires verification that no production code path calls the tested function and the test is not used to validate current behavior. Add clarity comment if preserved intentionally.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
