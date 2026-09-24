---
name: crossprovider codex scheduler-jobs-should-defer-heavy-client-imports
description: Scheduler jobs should defer heavy client imports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduler, lazy-imports, dependency-management]
---

Scheduler job modules should avoid top-level imports of heavy/optional domain clients. Use lazy import inside `_client_or_acquirer()` or `run()` to defer instantiation until the job actually executes, so job registration and CLI startup don't fail when dependencies aren't installed yet. Pattern: `HseRefreshJob` in worldenergydata-scheduler.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
