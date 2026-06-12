---
name: crossprovider codex error-suppression-in-state-mirroring-breaks-down
description: Error suppression in state-mirroring breaks downstream hooks
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-scripting, hooks, error-handling, observability]
---

When non-fatal operations (e.g., writing state files) are fully suppressed with `2>/dev/null || true`, downstream hooks depending on that state can silently malfunction without visibility into the root cause. For integration code, prefer failing visibly or logging a diagnostic even for non-fatal failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
