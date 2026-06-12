---
name: crossprovider hermes placeholder-formulas-block-gate-validation
description: Placeholder formulas block gate validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, source-gates, acceptance-criteria]
---

OCIMF-inspired / generic-tanker / stub values in acceptance-critical fields cause tests to contradict (tests pass but requirements unmet). Gate must fail-closed: reject placeholders at validation time, not warn. Absence of vessel-specific source citation is a blocker.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
