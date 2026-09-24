---
name: crossprovider codex scheduled-tasks-must-use-read-only-semantics
description: Scheduled tasks must use read-only semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduling, safety, read-only-semantics]
---

Cron/scheduled tasks should not call writeful scripts (e.g., anything that modifies state). Use read-only adapters or normalized views of existing data. Direct side-effect scripts in scheduled paths lead to safety issues, idempotence failures, and unpredictable artifact drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
