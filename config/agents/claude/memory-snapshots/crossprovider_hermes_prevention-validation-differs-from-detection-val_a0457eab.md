---
name: crossprovider hermes prevention-validation-differs-from-detection-val
description: Prevention validation differs from detection validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, tdd, safety-semantics]
---

TDD for 'prevent closed-issue routing' requires offline-mode regression tests (generators produce safe output without live validation), not just a separate pre-closeout validator. Detection-only (validate at closeout time) leaves normal generation unsafe if validation is skipped. Acceptance criteria must mandate both code safety and offline test coverage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
