---
name: crossprovider gemini ci-install-path-divergence-from-local-dev
description: CI install path divergence from local dev
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci-cd, python-packaging, testing]
---

Dependencies declared in `pyproject.toml` (even in `[project.optional-dependencies]`) don't guarantee they're available in CI unless the CI install step explicitly pulls them. `--all-extras` in uv should work, but verify locally in the same environment CI uses before assuming a missing-fixture error is a collection/plugin issue.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
