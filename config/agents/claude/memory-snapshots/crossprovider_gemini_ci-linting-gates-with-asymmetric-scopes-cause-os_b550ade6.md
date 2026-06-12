---
name: crossprovider gemini ci-linting-gates-with-asymmetric-scopes-cause-os
description: CI linting gates with asymmetric scopes cause os-specific failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci, linting, matrix-workflows]
---

When CI applies different tool scopes (e.g., `flake8 .` on repo root while `mypy src/` on package only), failures distribute unevenly across OS matrices. assethold example: linux/macos fail flake8 (root-level auxiliary files), windows fails mypy (package typing). Scope gates uniformly or accept asymmetric failure patterns.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
