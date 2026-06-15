---
name: crossprovider codex pep-723-scripts-in-sandbox-need-explicit-uv-cach
description: PEP-723 scripts in sandbox need explicit UV_CACHE_DIR
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [python-tooling, sandbox-environment, pep-723]
---

When running `uv run` on PEP-723 scripts in a sandbox or restricted environment, set `UV_CACHE_DIR=/tmp/uv-cache` explicitly to avoid read-only cache errors. The default `~/.cache/uv` may be unavailable or stale; a writable temp location ensures reproducible runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
