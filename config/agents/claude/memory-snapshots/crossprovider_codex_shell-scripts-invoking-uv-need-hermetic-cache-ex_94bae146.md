---
name: crossprovider codex shell-scripts-invoking-uv-need-hermetic-cache-ex
description: Shell scripts invoking uv need hermetic cache export
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-scripting, sandbox-execution, uv-policy]
---

Scripts calling `uv run` must export `UV_CACHE_DIR=${UV_CACHE_DIR:-$REPO_ROOT/.cache/uv}` at the top to ensure sandbox/CI hermeticity. Unwritable default cache causes silent failure (uv parser errors return 0 when followed by || echo 0), masking broken audit logic. WRK-1053 required this fix on two separate audit scripts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
