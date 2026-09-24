---
name: crossprovider gemini work-queue-location-is-a-single-governance-point
description: Work-queue location is a single governance point to prevent routing ambiguity
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, work-queue, enforcement]
---

WRK-*.md files must exist only in `.claude/work-queue/` (pending/working/blocked subdirs), never in docs or spec trees. Multiple sources of truth create agent routing confusion and metadata drift. Location audit + CI enforcement gate required.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
