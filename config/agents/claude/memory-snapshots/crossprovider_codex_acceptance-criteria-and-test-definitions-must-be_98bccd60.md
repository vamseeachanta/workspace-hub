---
name: crossprovider codex acceptance-criteria-and-test-definitions-must-be
description: Acceptance criteria and test definitions must be adversarially aligned
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-consistency, acceptance-criteria, adversarial-review]
---

A plan stated validators reject 'raw cat, recursive grep, os.walk' but then proposed tests violating exactly those patterns. Tests define reality; prose drifts. Run adversarial alignment checks: if acceptance criterion says X is forbidden, verify no proposed test would violate it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
