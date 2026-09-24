---
name: crossprovider codex cron-task-evidence-contracts-require-dual-valida
description: Cron task evidence contracts require dual validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, monitoring, evidence-contracts, task-health]
---

Declared `log:` globs in schedule configurations must be validated against actual emitted artifact paths. Tasks can emit non-log artifacts (markdown, JSON) or fail before reaching logging logic, causing false-green health status. Validate both declared glob and actual artifact location before assuming task success.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
