---
name: crossprovider hermes nested-git-status-timeouts-on-workspace-hub-unde
description: Nested git status timeouts on workspace-hub under Hermes load; use scoped queries
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-performance, nested-repo, workspace-hub]
---

`git status -z -uall` hangs; workaround with `git -c status.showUntrackedFiles=no status --short` or path-scoped `git diff -- <dir>` instead. Confirmed recurring under multi-agent parallel I/O.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
