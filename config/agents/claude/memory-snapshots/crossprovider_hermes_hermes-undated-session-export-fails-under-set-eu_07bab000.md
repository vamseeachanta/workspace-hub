---
name: crossprovider hermes hermes-undated-session-export-fails-under-set-eu
description: Hermes undated session export fails under set -euo pipefail
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, shell-scripting, set-euo-pitfall]
---

The pattern `grep -oE '[0-9]{8}' | head -1` exits nonzero when no date matches (e.g., files like `session_bg_22fe54.json`), blocking the entire pipeline under strict bash. Guard with `|| true` or empty-date check before the grep, or use `grep -oE '...' || echo ''` to provide a fallback.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
