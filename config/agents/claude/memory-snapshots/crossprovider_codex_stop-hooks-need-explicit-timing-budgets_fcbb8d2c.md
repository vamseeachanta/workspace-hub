---
name: crossprovider codex stop-hooks-need-explicit-timing-budgets
description: Stop hooks need explicit timing budgets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, hooks, user-experience]
---

Cleanup/maintenance scripts that run in stop hooks or cron must complete in <5s to avoid blocking interactive sessions. Include timing verification in tests (`time bash scripts/hooks/...` → <5s). For longer operations, defer to background cron instead of blocking hook.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
