---
name: crossprovider codex prefer-uv-over-system-python-for-reproducibility
description: Prefer uv over system python for reproducibility
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reproducibility, python-tooling, cross-machine]
---

SSoT and multi-machine tools should always run Python through `uv run --no-project` when uv exists, not system `python3` with globally-installed packages. System python introduces non-reproducible drift across machines, breaking the SSoT contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
