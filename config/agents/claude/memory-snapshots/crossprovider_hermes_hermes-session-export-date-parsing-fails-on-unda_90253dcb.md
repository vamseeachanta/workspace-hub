---
name: crossprovider hermes hermes-session-export-date-parsing-fails-on-unda
description: Hermes session export date parsing fails on undated files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-session-export, bash-regex-edge-case, date-extraction]
---

`scripts/cron/hermes-session-export.sh` fails silently when encountering undated Hermes session files (e.g., `session_bg_22fe54.json`). The `grep -oE '[0-9]{8}' | head -1` exits nonzero under `set -euo pipefail` before the empty-date guard clause. Fix: anchor regex to `^session_[0-9]{8}_` prefix or handle nonzero grep exit explicitly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
