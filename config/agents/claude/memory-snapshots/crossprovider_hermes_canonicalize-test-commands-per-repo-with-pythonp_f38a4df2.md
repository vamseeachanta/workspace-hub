---
name: crossprovider hermes canonicalize-test-commands-per-repo-with-pythonp
description: Canonicalize test commands per repo with PYTHONPATH variants
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, python, repo-specific]
---

Each tier-1 repo has distinct test invocation: `uv run pytest`, `PYTHONPATH=src uv run pytest`, `PYTHONPATH='src:../assetutilities/src' uv run pytest --noconftest`, etc. Variations required for import resolution; codify as canonical to prevent test-environment regressions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
