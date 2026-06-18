---
name: crossprovider codex codex-5-hour-percentage-is-used-percent-not-rema
description: Codex 5-hour percentage is used-percent, not remaining—requires inverse polarity
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [statusline, codex, quota, polarity, display]
---

Live Codex producer emits `.primary.usedPercent` (used), not remaining. When mapping to `five_hour_pct` cache field, apply inverse polarity: usedPercent=1 → cache=1 → render as 5h99%. Same inversion as Claude seven_day. Cited in query-codex-usage.sh and session payload `.rate_limits.primary.used_percent`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
