---
name: crossprovider codex time-base-mismatches-split-evidence-across-file-
description: Time-base mismatches split evidence across file boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [logging, timestamps, cron, evidence-tracking]
---

When cron scheduling and wrapper logging use different time formats or bases (e.g., `$(date +%Y-%m-%d)` vs `date -u`), evidence can split across separate files near midnight boundaries, complicating failure diagnosis. Normalize time bases between outer redirection and wrapper logging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
