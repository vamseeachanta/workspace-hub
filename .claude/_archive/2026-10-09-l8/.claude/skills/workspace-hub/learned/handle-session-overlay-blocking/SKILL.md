---
name: handle-session-overlay-blocking
description: Technique for dismissing overlay dialogs that freeze rendering and block form interaction in web automation
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["web-automation", "debugging", "javascript", "overlay-handling"]
---

# Handle Session Overlay Blocking

When a web session becomes unresponsive with blank/frozen screens, an overlay dialog (often session timeout) is likely blocking interaction. Use JavaScript to identify the blocking element (inspect DOM for overlay classes like `small_medium_overlay`), hide it with `display: none`, and scroll to reveal the form content. If screenshots fail due to overlay, verify form values via JavaScript inspection before submitting directly via `click()` rather than relying on visual verification.