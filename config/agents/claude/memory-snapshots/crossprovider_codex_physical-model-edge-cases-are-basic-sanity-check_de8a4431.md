---
name: crossprovider codex physical-model-edge-cases-are-basic-sanity-check
description: Physical-model edge cases are basic sanity checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hydrodynamics, validation, correctness, physics]
---

Zero-parameter cases (zero dihedral → expect sway force, not zero; zero advance ratio → expect static thrust) are basic validation that catch axis-mapping inversions and sign errors. Missing these checks allows physically inverted models to pass review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
