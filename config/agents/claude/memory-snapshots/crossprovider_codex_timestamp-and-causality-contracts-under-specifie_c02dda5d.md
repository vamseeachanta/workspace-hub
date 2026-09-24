---
name: crossprovider codex timestamp-and-causality-contracts-under-specifie
description: Timestamp and causality contracts under-specified in policy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [policy-review, timestamp-handling, causality]
---

Policies involving revert detection, approval timing, or event sequencing systematically fail to define timestamp sources, normalization, comparability, and tie-break rules. Require explicit timestamp contracts and single canonical event-ordering rules in any policy with causality reasoning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
