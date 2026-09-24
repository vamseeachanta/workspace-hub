---
name: crossprovider gemini ci-gate-asymmetry-causes-matrix-specific-hard-to
description: CI gate asymmetry causes matrix-specific, hard-to-diagnose failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-design, linting, testing]
---

When linters target different scopes (flake8 on root, mypy on src/), it produces asymmetric matrix failures across OSes. Define consistent, bounded package surfaces across all gates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
