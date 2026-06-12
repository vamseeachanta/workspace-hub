---
name: crossprovider codex bandit-toml-support-requires-explicit-toml-extra
description: Bandit TOML support requires explicit [toml] extra
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bandit, tooling, static-analysis, dependency-pinning]
---

Plain `bandit==1.9.4` will not reliably read TOML config from pyproject.toml; requires `bandit[toml]==1.9.4`. Common gotcha when pinning tool versions that have optional extras for config format support.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
