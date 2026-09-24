---
name: crossprovider codex hermes-session-export-filename-convention-and-gr
description: Hermes session export filename convention and graceful-skip pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hermes, shell-scripting, error-handling, filename-format]
---

Hermes session files follow `YYYYMMDD_<id>.json` dating convention. Export scripts using `set -euo pipefail` must make date-extraction guards no-match-safe (regex fail-soft) before any error guard; undated files should skip silently, not abort. Only date-parsing errors (not extraction misses) should remain fail-closed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
