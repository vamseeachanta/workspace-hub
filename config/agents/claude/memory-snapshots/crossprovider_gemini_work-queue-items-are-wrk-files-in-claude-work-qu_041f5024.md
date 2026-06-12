---
name: crossprovider gemini work-queue-items-are-wrk-files-in-claude-work-qu
description: Work queue items are WRK-* files in .claude/work-queue/, not YAML/JSON
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workspace-hub, work-queue, required-gate, task-tracking]
---

Plans that reference work-queue structure as `.yaml` or `.json` files miss that tasks are tracked as `WRK-*` files. Required Gate 1 for workspace-hub: every plan must map to a `WRK-*` ticket before implementation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
