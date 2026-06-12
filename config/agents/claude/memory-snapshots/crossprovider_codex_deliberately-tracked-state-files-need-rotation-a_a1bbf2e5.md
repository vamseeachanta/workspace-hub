---
name: crossprovider codex deliberately-tracked-state-files-need-rotation-a
description: Deliberately-tracked state files need rotation and pre-commit guards
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-state, size-limits, rotation]
---

State files (e.g., cost-tracking.jsonl) intentionally git-tracked for learning pipelines cannot be fixed via .gitignore. They need pre-commit size checks (e.g., 90 MB hard limit, 50 MB warning) and rotation policies to prevent push failures on large repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
