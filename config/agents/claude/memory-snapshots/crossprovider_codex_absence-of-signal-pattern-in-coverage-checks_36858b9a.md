---
name: crossprovider codex absence-of-signal-pattern-in-coverage-checks
description: Absence-of-signal pattern in coverage checks
metadata:
  type: reference
  source: codex
  bridged: 2026-08-02
  tags: [testing, guards, defect-pattern]
---

Guards that sum a subset of targets (e.g., 3 of 7 files) and pass if the others don't exist create a specific failure mode: missing or new targets silently pass coverage. Require explicit target membership derivation or an allowlist, not implicit coverage via absence. Defect class from issue #3761.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
