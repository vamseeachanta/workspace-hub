---
name: crossprovider codex shell-strict-mode-pipes-need-guards-before-extra
description: Shell strict-mode pipes need guards BEFORE extraction, not after
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell, cron, strict-mode, error-handling]
---

Under `set -euo pipefail`, guards for optional input formats must execute before piped expressions that could fail on no-match. Pattern: check input existence/type before piping to extraction (grep/awk); do NOT extract-then-conditionally-skip. For optional filenames, use extract-with-fallback (`${var:-default}`) rather than extract-and-guard.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
