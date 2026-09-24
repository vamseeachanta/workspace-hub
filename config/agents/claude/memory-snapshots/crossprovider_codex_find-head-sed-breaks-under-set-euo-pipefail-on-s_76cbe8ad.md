---
name: crossprovider codex find-head-sed-breaks-under-set-euo-pipefail-on-s
description: find | head | sed breaks under set -euo pipefail on SIGPIPE
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell, error-handling, pipefail]
---

In `set -euo pipefail`, the common pipeline `find ... | head | sed` fails because `head` closes the pipe, causing `find` to exit with SIGPIPE (non-zero status). Accumulate into an array, use `find ... -print0 | head -z`, or handle SIGPIPE explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
