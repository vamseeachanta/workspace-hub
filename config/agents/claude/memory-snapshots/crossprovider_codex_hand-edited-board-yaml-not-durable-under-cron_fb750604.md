---
name: crossprovider codex hand-edited-board-yaml-not-durable-under-cron
description: Hand-edited board YAML not durable under cron
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [durability, automation, labels, cron]
---

Cron workflow hard-resets to origin/main and reconciles from GitHub labels only. Manual card moves in board YAML are overwritten unless the live GitHub labels already drive the same placement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
