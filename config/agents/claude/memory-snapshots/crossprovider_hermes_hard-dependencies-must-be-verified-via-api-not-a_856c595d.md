---
name: crossprovider hermes hard-dependencies-must-be-verified-via-api-not-a
description: Hard dependencies must be verified via API, not assumed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependency-verification, spec-validation, first-run-green]
---

For install specs claiming first-run-green (e.g., uv.lock), verify the file exists via gh api before approval. A 404 on gh api repos/<repo>/contents/uv.lock invalidates the spec and any green-run claim built on it.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
