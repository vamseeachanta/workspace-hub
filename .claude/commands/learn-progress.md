---
name: learn-progress
description: "Show learning progress dashboard — how many tips seen per category, coverage percentages, days to full rotation."
model: haiku
effort: low
---

Show the learning progress overview:

!`uv run scripts/productivity/daily-learning.py --progress 2>/dev/null`

Then show tips by category:

!`uv run scripts/productivity/daily-learning.py --categories 2>/dev/null`

Summarize: which category has the lowest coverage? Suggest focusing practice there.
