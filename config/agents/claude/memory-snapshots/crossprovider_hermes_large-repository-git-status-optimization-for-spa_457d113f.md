---
name: crossprovider hermes large-repository-git-status-optimization-for-spa
description: Large repository git status optimization for sparse checkouts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, performance, sparse-checkout, large-repo]
---

When working with extremely large sparse-checkout repositories (360K+ files), `git status` hangs due to untracked file enumeration. Use `git -c status.showUntrackedFiles=no status` to suppress untracked files and complete in reasonable time. This applies to repos like acma-projects that trade complete materialization for selective checkout.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
