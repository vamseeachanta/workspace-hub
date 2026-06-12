---
name: crossprovider gemini sibling-repo-path-dependencies-require-explicit-
description: Sibling-repo path dependencies require explicit checkout in CI
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci-patterns, uv-sources, multi-repo-install]
---

When `pyproject.toml` declares `[tool.uv.sources] package = { path = "../sibling" }`, hosted CI runners (GitHub Actions) have no `../sibling` directory. Solution: add explicit `actions/checkout@v4` step with `path: ../sibling` to materialize the sibling repo before dependency install.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
