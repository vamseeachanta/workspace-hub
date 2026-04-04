---
name: feedback_html_refresh
description: HTML review files have 30s auto-refresh — regenerate the file instead of opening new browser tabs
type: feedback
---

HTML review/report files have 30s auto-refresh (`<meta http-equiv="refresh" content="30">`). Do NOT call `xdg-open` repeatedly — just regenerate the HTML and the existing browser tab auto-updates.

**Why:** Opening a new tab each time is redundant when the HTML already auto-refreshes.

**How to apply:** Open the HTML once (first time), then on subsequent regenerations just write the file — the browser picks up changes within 30s.
