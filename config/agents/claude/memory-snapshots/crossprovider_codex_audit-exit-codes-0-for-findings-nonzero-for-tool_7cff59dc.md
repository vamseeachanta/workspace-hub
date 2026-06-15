---
name: crossprovider codex audit-exit-codes-0-for-findings-nonzero-for-tool
description: Audit exit codes: 0 for findings, nonzero for tooling failure only
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, observability, exit-codes]
---

Read-only audits should exit 0 when complete, carrying OK/WARN/ERROR only in evidence lines and JSON state. Nonzero exits reserved for audit tooling failures (crashes, permission denials), not for discovering repo drift. Prevents false cron failures on ordinary state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
