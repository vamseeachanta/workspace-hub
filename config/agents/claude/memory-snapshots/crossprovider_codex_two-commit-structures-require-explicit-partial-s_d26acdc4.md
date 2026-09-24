---
name: crossprovider codex two-commit-structures-require-explicit-partial-s
description: Two-commit structures require explicit partial-state analysis
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, commit-safety, rollback-testing]
---

When a plan splits work into two commits (e.g., jumper retrofit + gallery link), ask: if Commit 1 ships and Commit 2 stalls, does production enter a state worse than pre-plan baseline? If Commit 1 is reverted after Commit 2 lands, is consistency broken? Unanswered, this is MAJOR.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
