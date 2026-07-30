---
name: crossprovider codex partial-test-harness-extracts-create-false-green
description: Partial test harness extracts create false-green
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, regression, contract-testing]
---

When a test harness extracts only a portion of a real workflow (e.g., render/finalize block) and pre-seeds derived variables, it masks failures in ordering, argument propagation, and full error semantics. Substring assertions also hide exact-argument mismatches. Full-workflow testing (real sequence, no pre-seeding) is required for acceptance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
