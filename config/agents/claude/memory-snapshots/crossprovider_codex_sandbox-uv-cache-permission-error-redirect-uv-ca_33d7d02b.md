---
name: crossprovider codex sandbox-uv-cache-permission-error-redirect-uv-ca
description: Sandbox uv cache permission error; redirect UV_CACHE_DIR to fix
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [testing, environment, tool-quirk]
---

`uv run` tests fail with permission errors on `/home/vamsee/.cache/uv` in sandboxed/restricted environments. Redirect with `UV_CACHE_DIR=.claude/state/uv-cache bash test.sh` to run in worktree; direct `python3 -m py_compile` also works as fallback.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
