---
name: crossprovider gemini session-locks-are-audit-trails-not-enforcement-m
description: Session locks are audit trails, not enforcement mechanisms
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [concurrency, auditing, lifecycle]
---

Session lock (PID/hostname/status) is written for observability and post-crash diagnosis, not to prevent concurrent access. Actual prevention comes from atomic file operations. Lock lifecycle: written at Stage 1 with status=in_progress, updated to status=claimed on successful claim, never deleted (audit trail).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
