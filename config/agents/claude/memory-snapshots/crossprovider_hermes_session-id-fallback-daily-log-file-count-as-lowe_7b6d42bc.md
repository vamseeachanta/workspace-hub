---
name: crossprovider hermes session-id-fallback-daily-log-file-count-as-lowe
description: Session ID fallback: daily log file count as lower_bound_active_days
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [observability, session-tracking, fallback-strategy]
---

Claude orchestrator raw logs lack stable session_id fields; counting session_YYYYMMDD files as lower_bound_active_days is safer than zero or untrustworthy estimates. Trade off: undercounts multi-session days but avoids false-zero metrics that hide actual activity.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
