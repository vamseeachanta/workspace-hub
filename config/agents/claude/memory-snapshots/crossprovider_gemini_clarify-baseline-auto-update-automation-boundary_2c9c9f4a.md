---
name: crossprovider gemini clarify-baseline-auto-update-automation-boundary
description: Clarify baseline auto-update automation boundary
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [quality, automation-boundary, tdd]
---

When a quality ratchet auto-updates baselines on improvement (coverage, mypy, etc.), explicitly define ownership: does the ratchet auto-stage/commit the baseline YAML, or require manual inclusion in commits? Undefined boundaries cause silent drift in tracked files and ambiguous CI behavior.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
