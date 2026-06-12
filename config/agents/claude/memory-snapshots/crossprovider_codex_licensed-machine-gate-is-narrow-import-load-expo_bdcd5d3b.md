---
name: crossprovider codex licensed-machine-gate-is-narrow-import-load-expo
description: Licensed-machine gate is narrow import/load/export boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [licensing, gate-design, machine-boundary]
---

For licensed software (e.g., OrcFxAPI), the gate is proof of import/load/solve/export on licensed host only. Everything else (config validation, fixture generation, artifact parsing, reporting, CI checks) must run license-free on any machine. Define boundary explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
