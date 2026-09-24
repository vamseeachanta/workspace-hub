---
name: crossprovider codex operator-only-vs-ci-reproducible-gate-separation
description: Operator-only vs CI-reproducible gate separation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, ci-cd, operations, design-pattern]
---

Plan acceptance criteria should explicitly distinguish between gates that fire in CI/CD (reproducible, no secrets, no auth required) and gates that fire only in operator workflows (auth-dependent, local-state-dependent, credential-bearing). Conflating them breaks CI reproducibility and gate traceability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
