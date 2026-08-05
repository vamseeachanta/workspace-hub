---
name: crossprovider codex scalar-verdict-apis-cannot-enforce-report-wide-a
description: Scalar verdict APIs cannot enforce report-wide aggregation rules
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [api-design, verification, aggregation]
---

A `derive_status(correlation, quality, consensus)` API accepting single scalar values per dimension cannot enforce cross-DOF rules like 'any insufficient DOF → incomplete verdict'. Verdict APIs must either accept full evidence sets or explicitly document which aggregations they do not enforce.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
