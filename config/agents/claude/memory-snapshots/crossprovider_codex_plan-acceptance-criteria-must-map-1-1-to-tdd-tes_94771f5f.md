---
name: crossprovider codex plan-acceptance-criteria-must-map-1-1-to-tdd-tes
description: Plan acceptance criteria must map 1:1 to TDD tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [planning, tdd, acceptance-criteria]
---

Each acceptance item requires an exact test proving coverage; missing fields from schema (e.g., `hash` in provenance test) leaves acceptance unclosed. Don't declare acceptance items without naming the test that proves them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
