---
name: crossprovider codex staged-index-reads-are-more-reliable-than-workin
description: Staged-index reads are more reliable than working-tree reads in staged reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, review-process, verification]
---

For staged change reviews, use `git show :path` to read index blobs directly rather than working-tree files, which may be edited or stale. Index reads ensure review accuracy for exactly what would be committed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
