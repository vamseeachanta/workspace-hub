---
name: crossprovider codex inline-only-review-cannot-verify-external-state-
description: Inline-only review cannot verify external state; design plans to be verifiable offline
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-discipline, verification, plan-design]
---

Codex consistently flagged that adversarial review without tool access cannot affirmatively verify external claims (GitHub issue state, file existence, reproduction results). Plans stating 'verified from GitHub issue #603' or relying on command output as proof without specifying environment (branch, PYTHONPATH, clean state) create verification gaps. Structure plans so correctness-critical claims can be checked from the inline text or repository files alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
