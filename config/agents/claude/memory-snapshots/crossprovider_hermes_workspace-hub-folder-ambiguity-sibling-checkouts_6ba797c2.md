---
name: crossprovider hermes workspace-hub-folder-ambiguity-sibling-checkouts
description: Workspace-hub folder ambiguity: sibling checkouts need explicit role classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workspace-organization, tier-1-repos, cleanup-contract]
---

/mnt/local-analysis/<tier-1-repo> checkouts (e.g., digitalmodel) coexist with workspace-hub repo structure, causing confusion. Classify each copy by role before sync/cleanup: primary-working-copy, secondary-working-copy, read-only-reference, ephemeral-worktree, artifact-cache, or fail-closed as unknown.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
