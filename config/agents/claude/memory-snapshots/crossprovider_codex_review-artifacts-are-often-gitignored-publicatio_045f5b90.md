---
name: crossprovider codex review-artifacts-are-often-gitignored-publicatio
description: Review artifacts are often gitignored; publication requires explicit force-add
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [git-workflow, publication, artifact-management]
---

Adversarial review artifacts for issue #3549 were gitignored and required exact-path force-add to commit. Don't assume artifacts auto-land; confirm whether they're tracked, staged, and part of the publication plan before considering the review complete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
