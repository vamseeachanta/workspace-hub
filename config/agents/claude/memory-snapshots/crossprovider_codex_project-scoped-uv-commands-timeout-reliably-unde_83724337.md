---
name: crossprovider codex project-scoped-uv-commands-timeout-reliably-unde
description: Project-scoped uv commands timeout reliably under workspace contention
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workspace-contention, validation-performance, uv-workaround]
---

Commands like `uv run pytest` hang frequently when the workspace is under load; `uv run --no-project` with explicit dependencies is faster. Set explicit timeout bounds (30s–300s) to prevent hung processes from consuming worker slots, then fall back to narrower validation paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
