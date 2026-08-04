---
name: crossprovider codex batch-cloned-repos-are-hidden-duplication-in-wor
description: Batch-cloned repos are hidden duplication in work surfaces
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [duplication, work-surface-hygiene, batch-jobs, git-clones]
---

In engineering work surfaces, repos cloned multiple times with batch/phase naming (e.g., wed-batch5, phase2-batch3, wed-phase2-carve) are almost always pure duplication. At most one per origin should be KEEP; the rest should be removed unless they hold unmerged work or are actively used by jobs on that machine.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
