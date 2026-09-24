---
name: crossprovider gemini workspace-hub-uses-wrk-task-file-format-in-claud
description: workspace-hub uses WRK-* task file format in .claude/work-queue/
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workspace-hub, work-queue, file-format]
---

Work-queue tasks are stored as `WRK-*` files (e.g., `WRK-123.md`) in `.claude/work-queue/`, not YAML or JSON. Plans touching work-queue logic must parse and reference the actual WRK-* format, not generic config files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
