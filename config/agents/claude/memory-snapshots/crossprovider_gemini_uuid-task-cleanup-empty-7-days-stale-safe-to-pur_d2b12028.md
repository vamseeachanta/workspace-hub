---
name: crossprovider gemini uuid-task-cleanup-empty-7-days-stale-safe-to-pur
description: UUID task cleanup: empty + >7 days stale = safe to purge
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cleanup, uuid-validation, time-based-retention]
---

UUID regex (8-4-4-4-12 hex) identifies task dirs. Purge only if empty (ls -A) AND mtime >7 days. Prevents false positives on fresh empty dirs and catches true orphans. Used in tidy-agent-teams.sh as part of nightly cleanup.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
