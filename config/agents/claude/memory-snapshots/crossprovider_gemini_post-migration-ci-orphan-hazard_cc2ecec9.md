---
name: crossprovider gemini post-migration-ci-orphan-hazard
description: Post-migration CI orphan hazard
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci, migration, orphan-detection]
---

Large-scale repo migrations (WRK→GSD) often leave dangling script references in CI workflows (.github/workflows/*.yml) and pre-commit configs (.pre-commit-config.yaml). These cause persistent CI failure for weeks because the references are only checked at runtime. Explicitly audit CI configs against file existence after major refactors.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
