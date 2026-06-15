---
name: crossprovider codex silent-cron-failure-exits-0-breaks-observability
description: Silent cron failure exits 0, breaks observability
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, observability, workspace-hub]
---

equality-matrix cron exits 0 despite ModuleNotFoundError, suppressing alarms and stale dashboard. Self-healing reconcilers require loud failure detection (non-zero exit + notification) before write-enabled convergence. Pattern: every cron must fail non-zero on error and route failures to alerting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
