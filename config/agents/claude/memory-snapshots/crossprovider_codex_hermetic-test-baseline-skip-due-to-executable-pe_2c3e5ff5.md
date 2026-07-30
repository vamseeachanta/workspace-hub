---
name: crossprovider codex hermetic-test-baseline-skip-due-to-executable-pe
description: Hermetic test baseline: skip due to executable permission is a defect, not a feature
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, baseline-quality]
---

Tests that skip because tracked files lack executable mode or depend on live GitHub clone state are not hermetic. Fold baseline defects into issue plans explicitly so metadata-only contracts can be tested deterministically in isolation, not inherited from false-green harnesses.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
