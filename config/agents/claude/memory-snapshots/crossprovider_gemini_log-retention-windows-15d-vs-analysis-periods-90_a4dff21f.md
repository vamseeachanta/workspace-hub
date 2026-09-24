---
name: crossprovider gemini log-retention-windows-15d-vs-analysis-periods-90
description: Log retention windows (15d) vs analysis periods (90d) create false positives
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [logging, time-windows, state-management]
---

Session logs are rotated after ~15 days, so usage checks beyond that window (e.g., `invocations_90d == 0`) will produce false negatives. Track persistent state or reduce the window to match retention.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
