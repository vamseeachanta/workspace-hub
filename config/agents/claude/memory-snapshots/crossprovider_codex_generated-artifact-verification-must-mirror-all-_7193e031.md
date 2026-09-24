---
name: crossprovider codex generated-artifact-verification-must-mirror-all-
description: Generated artifact verification must mirror all pipeline steps or it flags legitimate appended content as drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, generators, verification-parity, regression-prevention]
---

A drift checker that rebuilds shared+delta body but omits generated appends (e.g., provider-specific skill index) falsely flags valid output as out-of-sync. Post-generation tests must include every modification the builder performs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
