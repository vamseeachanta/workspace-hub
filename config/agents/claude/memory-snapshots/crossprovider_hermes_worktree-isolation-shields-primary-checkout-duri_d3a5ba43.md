---
name: crossprovider hermes worktree-isolation-shields-primary-checkout-duri
description: Worktree isolation shields primary checkout during concurrent writers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, safety, worktree, concurrent-ops]
---

When an active process (e.g., Claude PID 12020) is using the primary checkout, use a separate worktree (e.g., `/mnt/local-analysis/reconcile-main-<date>`) for reconciliation/recovery work instead of mutating the primary checkout in-place. This avoids merge races, lost work, and merge-state conflicts when the active process exits and resumes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
