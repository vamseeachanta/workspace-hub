---
name: crossprovider codex test-fixture-parametrization-isolates-independen
description: Test fixture parametrization isolates independent code paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [testing, fixture-isolation, parametrization]
---

When a test loops over multiple cases (e.g., orphan and fabricated identities), parametrized fixtures ensure each exercises its own shallow-to-deep hydration path independently. Shared fixture iteration can mask required conditions — the fabricated case may pass via early non-shallow rejection without proving post-fetch validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
