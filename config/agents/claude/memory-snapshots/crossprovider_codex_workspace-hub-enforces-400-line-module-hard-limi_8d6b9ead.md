---
name: crossprovider codex workspace-hub-enforces-400-line-module-hard-limi
description: workspace-hub enforces 400-line module hard limit
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [architecture, code-quality, workspace-hub]
---

Multiple style reviews flagged files exceeding 400 lines (session 3: 411-line card_generators.py and 430-line test file; session 18: 576-line report module). This is an architectural rule, not a guideline — modules should be split at this boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
