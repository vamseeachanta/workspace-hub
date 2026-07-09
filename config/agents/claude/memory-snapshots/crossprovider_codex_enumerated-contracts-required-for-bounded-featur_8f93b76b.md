---
name: crossprovider codex enumerated-contracts-required-for-bounded-featur
description: Enumerated contracts required for 'bounded' features
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [plan-review, contract-design, security-gate]
---

Plan reviews reject 'bounded' or 'closed' features specified as prose. Must provide explicit grammar (JSON schema, enum, predicate list) with test coverage. Observed in #67 firewall reviews: vague caps on manifest sampling triggered MAJOR findings across multiple reviewers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
