---
name: crossprovider hermes nested-repo-test-commands-require-explicit-pytho
description: Nested repo test commands require explicit PYTHONPATH and --noconftest flags
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-command, pythonpath, conftest]
---

Tier-1 repos have repo-scoped test commands (e.g., `digitalmodel`: `PYTHONPATH=src uv run python -m pytest`, `worldenergydata`: `PYTHONPATH='src:../assetutilities/src' uv run python -m pytest --noconftest`) that isolate test discovery and avoid parent conftest pollution. Update CI/local runs to match repo AGENTS.md contract.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
