---
name: crossprovider hermes deterministic-artifact-regeneration-for-validati
description: Deterministic artifact regeneration for validation and drift detection
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-validation, determinism, ci-patterns]
---

Comparing committed artifacts to freshly-generated versions (with deterministic output) catches drift and ensures consistency. Pattern applies to manifests, checksums, reports, schemas; should be part of standard CI validation alongside unit tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
