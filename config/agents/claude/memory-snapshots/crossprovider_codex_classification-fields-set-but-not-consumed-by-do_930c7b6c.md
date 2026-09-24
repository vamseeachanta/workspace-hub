---
name: crossprovider codex classification-fields-set-but-not-consumed-by-do
description: Classification fields set but not consumed by downstream code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, design-gaps, integration, correctness]
---

When refactoring to add a new classification or status field, verify it's actually consumed by dependent code. Unused fields often indicate incomplete refactoring or design misalignment, which can hide bugs or create maintenance debt.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
