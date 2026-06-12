---
name: crossprovider hermes local-pytest-invocation-diverges-from-ci
description: Local pytest invocation diverges from CI
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, ci-parity, assethold]
---

`pytest -c pyproject.toml --noconftest -o addopts=` (12.10% coverage) ≠ `uv run --project . python -m pytest` (60.70% coverage). Local validators without conftest/addopts/markers are not CI-parity. Always use `uv run --project` for local CI-parity checks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
