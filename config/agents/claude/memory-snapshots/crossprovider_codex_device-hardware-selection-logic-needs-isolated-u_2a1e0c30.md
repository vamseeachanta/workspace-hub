---
name: crossprovider codex device-hardware-selection-logic-needs-isolated-u
description: Device/hardware selection logic needs isolated unit test helpers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [testing, mocking, hardware-abstraction, unit-tests]
---

Testing capture-device selection or similar hardware-dependent logic should extract pure parsing/selection into small sourced shell libraries testable without running full installers or touching real devices. Helpers can be dual-use: define functions when sourced, or execute with `--choose` to print device to stdout or error reasons to stderr.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
