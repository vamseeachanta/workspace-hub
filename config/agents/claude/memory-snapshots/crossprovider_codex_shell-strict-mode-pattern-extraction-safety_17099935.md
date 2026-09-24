---
name: crossprovider codex shell-strict-mode-pattern-extraction-safety
description: Shell strict-mode pattern extraction safety
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, strict-mode, pattern-matching]
---

Parameter expansion pattern matches under `set -euo pipefail` abort if no match occurs. Guard with explicit `[[ ]]` test before accessing results; `|| true` in pipes does not catch parameter expansion failures. Critical when extracting structured data (dates, IDs) from filenames.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
