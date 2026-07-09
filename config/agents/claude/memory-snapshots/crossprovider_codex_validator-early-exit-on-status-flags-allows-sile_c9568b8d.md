---
name: crossprovider codex validator-early-exit-on-status-flags-allows-sile
description: Validator early-exit on status flags allows silent corruption
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [regression-testing, validation]
---

A validator that skips consistency checks for non-ready rows (implementation_ready=false) silently passes corrupted or swapped plan references. Even placeholder rows need status_snapshot and plan_path validation against their referenced documents.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
