---
name: crossprovider codex adversarial-review-verifies-artifact-claims-agai
description: Adversarial review verifies artifact claims against reality
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [review, verification, testing, correctness]
---

Don't trust plan citations; verify them: confirm file paths exist (via `find`/`ls`), check GitHub issue state (via `gh issue view`, retry with escalation if sandboxed), inspect actual repo state. Treat plan claims as assertions to verify, not facts. This catches cited artifacts that were deleted, renamed, or never merged.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
