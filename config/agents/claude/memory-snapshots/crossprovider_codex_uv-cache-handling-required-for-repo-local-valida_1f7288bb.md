---
name: crossprovider codex uv-cache-handling-required-for-repo-local-valida
description: UV cache handling required for repo-local validators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, environment, validation]
---

Running validators in the repo with default UV cache causes permission failures when tools try to write to ~/.cache. Set UV_CACHE_DIR=.uv-cache to use repo-local cache. This is environment-specific but recurs across validation commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
