---
name: crossprovider codex test-first-for-governance-gate-validation
description: Test-first for governance gate validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, governance, test-first]
---

When implementing governance gates (clearance checks, data-boundary validation, IP filters), write failing tests first that verify the gate works (e.g., tests fail if full-text is persisted, tests fail if clearance record missing). Post-condition checks alone are insufficient for TDD compliance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
