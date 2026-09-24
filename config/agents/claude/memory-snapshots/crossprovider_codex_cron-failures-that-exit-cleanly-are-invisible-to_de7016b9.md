---
name: crossprovider codex cron-failures-that-exit-cleanly-are-invisible-to
description: Cron failures that exit cleanly are invisible to monitoring
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, observability, automation, error-handling]
---

Scripts that catch errors internally but exit 0 (e.g., Python under `uv run` with uncaught exceptions) are unobservable. Drift accumulates silently. Must enforce non-zero exit and route failures to notification channels, or health/equivalence dashboards become stale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
