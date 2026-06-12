---
name: crossprovider codex count-only-violation-baselines-miss-regressions
description: Count-only violation baselines miss regressions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [baseline-gating, static-analysis, testing]
---

A baseline of 'X total findings' passes even if one issue was fixed and one new issue appeared (count unchanged). Violation gating needs stable finding identity (rule ID + severity + confidence + file + line) not just counts; counts alone are insufficient for regression detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
