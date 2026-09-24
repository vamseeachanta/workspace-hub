---
name: crossprovider gemini sibling-repo-dependencies-in-ci-require-explicit
description: Sibling repo dependencies in CI require explicit checkout
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-health, github-actions, uv, dependency-resolution]
---

Local path-relative dependencies declared in `[tool.uv.sources]` (e.g., `assetutilities = { path = "../assetutilities" }`) do not resolve on GitHub Actions runners. CI must use `actions/checkout` to explicitly fetch sibling repos into the expected local path structure to match dev layout.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
