---
name: crossprovider codex schema-vocabulary-mismatches-across-reusable-con
description: Schema vocabulary mismatches across reusable contracts are integration risks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [schema-reuse, vocabulary-alignment, integration-risk]
---

A plan reusing page-shape and wave0-ledger contracts didn't catch that `page_shape_parse_status_values` enums differed between `skills/page-shape-contract/SKILL.md` and the authoritative `artifacts/ace-wave0-ledger-schema.json`. This can break downstream validators or force silent enum rewrites. Plans reusing schema/contracts from other issues should include adversarial enum/vocabulary alignment verification in acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
