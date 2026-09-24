---
name: crossprovider codex flag-underivable-constants-rather-than-synthesiz
description: Flag underivable constants rather than synthesizing replacements
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [domain-constraint, constants, testing]
---

When domain physics values cannot be derived from repository evidence (e.g., correlation thresholds, phase tolerances, solver biases), leave them explicitly flagged as undefined rather than inventing fitted constants. This preserves a 'no fitted constants' constraint that allows later design/discovery without rewriting tested code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
