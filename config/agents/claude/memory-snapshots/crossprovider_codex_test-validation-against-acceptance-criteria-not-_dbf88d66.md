---
name: crossprovider codex test-validation-against-acceptance-criteria-not-
description: Test validation against acceptance criteria, not just happy path
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance-criteria, defect-pattern]
---

Tests passing on happy path while missing edge cases is a recurring defect. Acceptance criteria should explicitly drive edge case enumeration: fallback branches, non-canonical inputs, visibility constraints, wrong values. Maps test design to spec.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
