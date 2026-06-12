---
name: crossprovider hermes large-repos-360k-files-require-sparse-checkout-s
description: Large repos (360K+ files) require sparse checkout strategy
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-performance, large-repos, sparse-checkout]
---

Repos with 300K–400K files cause git pull/clone/status to timeout at ~120s. Workaround: use `--filter=blob:none`, sparse-checkout constraints, and avoid full materialization. Very large repos benefit from targeted `git ls-files` queries or `git show --name-status` instead of expensive `git status` scans.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
