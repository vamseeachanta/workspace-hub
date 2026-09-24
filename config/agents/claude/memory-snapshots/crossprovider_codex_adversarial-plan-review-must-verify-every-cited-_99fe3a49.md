---
name: crossprovider codex adversarial-plan-review-must-verify-every-cited-
description: Adversarial plan review must verify every cited file path exists at HEAD
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review, verification, planning]
---

Before approval, enumerate actual code paths via `git ls-files` or `git show HEAD:path`. Plans that name non-existent paths or use ambiguous basenames will miss live code during implementation; a single omitted consumer breaks the contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
