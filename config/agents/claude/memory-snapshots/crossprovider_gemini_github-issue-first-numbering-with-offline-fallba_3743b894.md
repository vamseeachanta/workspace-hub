---
name: crossprovider gemini github-issue-first-numbering-with-offline-fallba
description: GitHub-issue-first numbering with offline fallback beats dual-numbering
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [numbering, single-source-of-truth, offline-fallback]
---

GitHub is the single ID source (WRK-NNN where NNN = issue number). Offline fallback: create WRK-LOCAL-YYYYMMDD-HHMMSS with promote-local-ids.sh on reconnect. Eliminates confusion.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
