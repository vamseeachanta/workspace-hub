---
name: crossprovider gemini staleness-auto-enforcement-7-day-warning-14-day-
description: Staleness auto-enforcement: 7-day warning, 14-day critical move-back
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workflow, automation]
---

Items in `working/` > 7 days old get `stale: warning` tag; > 14 days get `stale: critical` and auto-move back to `pending/` with status reset. Call `check_stale_items()` on session init for passive enforcement.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
