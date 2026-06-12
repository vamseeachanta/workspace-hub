---
name: crossprovider gemini defensive-git-automation-timeout-status-tracking
description: Defensive git automation: timeout + status tracking
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git-automation, shell-scripting, reliability]
---

Use `git submodule status` instead of `foreach` to avoid hanging on detached submodules; apply per-command timeouts (5–10s); track results in arrays (succeeded/failed/timeout/skipped) for operational visibility. Prevents silent hangs in multi-repo workflows.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
