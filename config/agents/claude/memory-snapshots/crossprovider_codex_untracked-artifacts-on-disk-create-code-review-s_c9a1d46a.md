---
name: crossprovider codex untracked-artifacts-on-disk-create-code-review-s
description: Untracked artifacts on disk create code-review staging hazards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, code-review, artifact-tracking]
---

Implementation artifacts that exist on disk but remain untracked in Git create a critical gap: the review cannot validate what will actually land in the repository. A code-stage review must require that all deliverables are staged and tracked before sign-off; otherwise parent systems will over-claim completion based on stale metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
