---
name: crossprovider codex time-base-mismatch-splits-evidence-logs
description: Time-base mismatch splits evidence logs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cron, logging, time-synchronization]
---

When combining outer cron redirection with inner script logging, date formats must align (e.g., both `$(date +%Y-%m-%d)` vs `date -u`). Mismatches cause evidence to split across files near midnight, breaking health monitors and evidence contracts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
