---
name: crossprovider codex timestamp-gate-logic-needs-all-three-cases-expli
description: Timestamp gate logic needs all three cases explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gates, time, boundary-conditions]
---

Gate logic with temporal boundaries (e.g., legacy exemption based on creation date) must spell out all three cases: absent/malformed (fail), valid < cutoff (skip), valid ≥ cutoff (enforce). Implicit defaults or missing edge cases invite silent gate failures; equality at boundary must be stated explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
