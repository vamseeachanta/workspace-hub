---
name: crossprovider codex reusable-validation-facades-should-be-documented
description: Reusable validation facades should be documented and extracted before parallel implementation work
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [code-reuse, documentation, architecture]
---

When multiple issues are about to implement similar validation (e.g., token fixture checking, artifact scanning), the exploration phase should identify and document existing facades/APIs that avoid reimplementation divergence. Example: #63 found reusable `validate_public_artifact_paths` and token validators already present in #68.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
