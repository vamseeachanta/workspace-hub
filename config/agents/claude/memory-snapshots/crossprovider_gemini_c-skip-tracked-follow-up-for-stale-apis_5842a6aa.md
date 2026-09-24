---
name: crossprovider gemini c-skip-tracked-follow-up-for-stale-apis
description: C-skip + tracked follow-up for stale APIs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, technical-debt, closure-pattern, pragmatism]
---

When remediation requires domain knowledge or API paths unclear at review time, mark tests as skipped with an explicit follow-up issue rather than leaving them red or guessing a repoint. This pragmatic closure pattern unblocks CI while deferring remediation to someone with domain context.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
