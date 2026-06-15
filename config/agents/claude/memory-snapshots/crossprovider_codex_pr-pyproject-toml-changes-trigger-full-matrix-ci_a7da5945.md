---
name: crossprovider codex pr-pyproject-toml-changes-trigger-full-matrix-ci
description: PR pyproject.toml changes trigger full-matrix CI in digitalmodel
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ci, digitalmodel, architecture]
---

Any pyproject.toml or src/digitalmodel/ change runs all domain tests via detect_touched_domains.py. This exposes 13+ baseline-red suites (missing imports, stale paths, headless rendering, missing licensed assets) that are not CI-clean concurrently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
