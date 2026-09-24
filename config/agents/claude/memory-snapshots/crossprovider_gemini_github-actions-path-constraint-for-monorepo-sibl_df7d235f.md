---
name: crossprovider gemini github-actions-path-constraint-for-monorepo-sibl
description: GitHub Actions path constraint for monorepo sibling checkouts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci, github-actions, monorepo, dependencies]
---

actions/checkout@v4 enforces paths under $GITHUB_WORKSPACE; sibling repos outside that tree need `git clone` as fallback. Relevant when pyproject.toml declares `[tool.uv.sources] sibling = { path = "../sibling-repo" }` — such references fail on runners and require explicit pre-checkout of the sibling into ../path to match local dev layout.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
