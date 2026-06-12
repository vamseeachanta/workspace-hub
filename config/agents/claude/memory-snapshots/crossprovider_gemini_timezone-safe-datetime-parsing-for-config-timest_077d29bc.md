---
name: crossprovider gemini timezone-safe-datetime-parsing-for-config-timest
description: Timezone-safe datetime parsing for config timestamps
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, datetime, config-parsing]
---

For ISO 8601 timestamps in configs, normalize Z suffix explicitly (`.replace('Z', '+00:00')`) before `datetime.fromisoformat()` for Python 3.8+ compatibility. Always compare on UTC-aware `datetime` objects, not raw strings, to avoid offset/timezone bugs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
