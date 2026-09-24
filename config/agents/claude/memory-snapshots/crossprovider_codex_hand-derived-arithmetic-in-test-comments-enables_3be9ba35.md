---
name: crossprovider codex hand-derived-arithmetic-in-test-comments-enables
description: Hand-derived arithmetic in test comments enables independent verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, documentation]
---

When test fixtures include by-hand calculations and expected results (e.g., `2*sqrt(...)*sin(θ)/r = 395.3498 lb`), future reviewers can independently re-derive correctness without trusting implementation. This catches coefficient errors that test encoding would otherwise lock in.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
