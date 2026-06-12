---
name: crossprovider hermes root-workspace-must-not-edit-nested-tier-1-repos
description: Root workspace must not edit nested tier-1 repos; repos must not edit siblings
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-isolation, parallel-safety, branch-scoping]
---

Root `workspace-hub` changes and tier-1 repo work (assetutilities, digitalmodel, etc.) must not cross-edit. Use separate commits, branches, or worktrees to enforce isolation. Git lock races and silent change losses occur when parallel sessions edit different repos in the same working tree.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
