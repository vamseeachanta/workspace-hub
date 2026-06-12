---
name: crossprovider codex bash-strict-shell-date-timestamp-extraction-need
description: Bash strict-shell date/timestamp extraction needs no-match fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell, strict-mode, bash-patterns]
---

In `set -euo pipefail` scripts, regex-driven date extraction (e.g., from session basenames) must explicitly handle the no-match case before any guard. Undeclared variable abort is the failure mode. #2764 found `session_bg_22fe54` lacked 8-digit date and triggered immediate failure; fix requires `[[ $date ]]` or pattern-safe extraction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
