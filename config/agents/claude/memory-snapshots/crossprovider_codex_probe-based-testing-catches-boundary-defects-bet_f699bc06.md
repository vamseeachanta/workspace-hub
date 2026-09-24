---
name: crossprovider codex probe-based-testing-catches-boundary-defects-bet
description: Probe-based testing catches boundary defects better than test-name inference
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation, quality-assurance]
---

Unit test names suggest intent but don't prove behavior. Move beyond green test results to run direct runtime probes with synthetic malformed inputs: wrong types, missing keys, outside-boundary values. Probes against the actual code surface catch crash paths and edge cases that passing tests can miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
