---
name: crossprovider codex unconnected-helper-functions-mask-coverage-gaps
description: Unconnected helper functions mask coverage gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, coverage, integration, discovery]
---

A helper function that exists but is never called from entrypoints or tests represents a coverage defect. Verify wiring from entry points, not just existence; unused helpers hide missing instrumentation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
