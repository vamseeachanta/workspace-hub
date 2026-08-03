---
name: crossprovider codex test-coverage-via-parameter-freezing-masks-domai
description: Test coverage via parameter freezing masks domain-specific defects
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [test-coverage, hidden-defects, domain-specific, physics-testing]
---

Tests setting critical domain parameters to zero (e.g., gravity=0, density=0) to isolate one dimension can hide sign errors and datum transforms in derived quantities. Unit test with gravity=0 missed force-datum bug; similar approach masked Coulomb friction sign inversion in periodic boundary. Revalidate real-card acceptance metrics whenever defaults or activation paths change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
