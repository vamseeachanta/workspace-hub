---
name: crossprovider codex active-work-item-detection-via-directory-scan
description: Active work item detection via directory scan
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [work-tracking, directory-scan, context-tagging]
---

Tag session signals with active WRK context by scanning `.claude/work-queue/working/` for `WRK-*.md` files. Gives observability into which work items consume context and cost, useful for work-in-progress tracking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
