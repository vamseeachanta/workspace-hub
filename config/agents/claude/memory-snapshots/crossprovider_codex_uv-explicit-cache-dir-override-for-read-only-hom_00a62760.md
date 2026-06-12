---
name: crossprovider codex uv-explicit-cache-dir-override-for-read-only-hom
description: UV explicit cache dir override for read-only $HOME/.cache in Codex
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [uv, codex, sandbox, environment, cache]
---

Codex sandboxes often restrict `$HOME/.cache` write access; `uv run` silently fails on cache index creation. Prepend all `uv` commands with `UV_CACHE_DIR=/tmp/uv-cache UV_LINK_MODE=copy` to force writable temporary cache and avoid cache-related hangs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
