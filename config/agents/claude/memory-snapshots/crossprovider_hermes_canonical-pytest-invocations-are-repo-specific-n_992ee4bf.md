---
name: crossprovider hermes canonical-pytest-invocations-are-repo-specific-n
description: Canonical pytest invocations are repo-specific; not generic
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, pytest, repo-structure]
---

Each repo requires distinct pytest calls: assetutilities `uv run python -m pytest tests`, digitalmodel `PYTHONPATH=src uv run python -m pytest`, worldenergydata `PYTHONPATH='src:../assetutilities/src' uv run python -m pytest --noconftest`, assethold `uv run python -m pytest tests/ --noconftest`. Missing PYTHONPATH or --noconftest flags causes conftest pollution or import failures. Lookup per-repo, do not guess.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
