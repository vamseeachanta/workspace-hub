---
name: crossprovider codex empty-activity-must-flag-no-activity-status-not-
description: Empty activity must flag no-activity status, not fall back to calendar span
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [correctness, missing-data, rig-days]
---

When a bore has no WAR rows for a target activity code, return pd.NA (missing data) with explicit status, not zero or fall through to calendar spud-to-TD. Empty WAR is not evidence of zero rig days.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
