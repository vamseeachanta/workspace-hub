---
name: crossprovider hermes artifact-repo-root-inference-must-be-scoped-to-c
description: Artifact repo-root inference must be scoped to cwd, not climb parents
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-validation, scoping, test-isolation]
---

Repo root inference for artifact validation (e.g., to fill in default freshness) should only trigger if artifact/report are relative to current working directory. Climbing parent directories causes false inferences in tests with temp directories.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
