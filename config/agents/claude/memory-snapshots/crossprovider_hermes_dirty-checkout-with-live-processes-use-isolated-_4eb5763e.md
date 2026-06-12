---
name: crossprovider hermes dirty-checkout-with-live-processes-use-isolated-
description: Dirty checkout with live processes: use isolated reconciliation, not rebase
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, multi-session, workspace-management]
---

When primary checkout (`/mnt/local-analysis/workspace-hub`) has live Claude/Hermes processes with cwd inside, avoid direct `git rebase/reset`. Instead, use an isolated reconciliation checkout in `/mnt/local-analysis/reconcile-*`, commit/push there, then let live processes fetch/rebase when idle. Directly rebasing will contend with active git operations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
