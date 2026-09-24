---
name: crossprovider codex cross-repo-plan-verification-requires-sibling-ch
description: Cross-repo plan verification requires sibling checkout access
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, cross-repo, plan-review]
---

When verifying plans that cite paths in sibling repositories, those paths may not exist in the primary working directory. Always verify claims against actual sibling checkouts directly rather than assuming cited artifacts are present in the current repo.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
