---
name: crossprovider hermes naval-arch-tdd-tests-need-synthetic-ocimf-derive
description: Naval-arch TDD tests need synthetic OCIMF-derived placeholder data to avoid licensed-corpus leakage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [naval-architecture, test-data, licensing, proj-a, tdd]
---

proj-a force calculation tests cannot use real OCIMF MEG 4 coefficients (licensed material). TDD tests must use placeholder domain `"OCIMF-derived"` with synthetic force/moment values to pass source-gate checks, enabling coordinate/sign-convention and component-order validation without committing proprietary data.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
