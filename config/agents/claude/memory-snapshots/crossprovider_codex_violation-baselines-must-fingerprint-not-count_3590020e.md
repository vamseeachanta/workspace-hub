---
name: crossprovider codex violation-baselines-must-fingerprint-not-count
description: Violation baselines must fingerprint, not count
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [baseline-design, regression-detection, gating-pattern]
---

Count-based baselines miss regressions: one old finding removed + one new found = same count but regressed state. Track rule ID + file + line + message hash instead; Bandit's native JSON baseline is a good reference implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
