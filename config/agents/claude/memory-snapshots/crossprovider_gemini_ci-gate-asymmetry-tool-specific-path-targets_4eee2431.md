---
name: crossprovider gemini ci-gate-asymmetry-tool-specific-path-targets
description: CI gate asymmetry (tool-specific path targets)
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci, linting, gates]
---

When linting multi-surface repos, lint tools may target different depths (flake8 . vs mypy src/), creating asymmetric failure surfaces. Explicitly define symmetric paths and exclude auxiliary directories (.agent-os/, scripts/) from main package gates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
