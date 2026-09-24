---
name: crossprovider codex external-dependencies-require-registry-pinned-re
description: External dependencies require registry-pinned revisions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, versioning, reproducibility]
---

Mutable-main consumption from external datasets (e.g., HuggingFace latest) breaks reproducibility. Revision pins must live in the project's registry/manifest, not as automatic-latest references or self-referential mutable pointers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
