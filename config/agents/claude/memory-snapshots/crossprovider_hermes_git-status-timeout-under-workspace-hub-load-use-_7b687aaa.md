---
name: crossprovider hermes git-status-timeout-under-workspace-hub-load-use-
description: Git status timeout under workspace-hub load — use scoped diffs + ls-remote
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-operations, workspace-hub-scale, operational-pattern]
---

Broad `git status` hangs in busy workspace-hub (30+ concurrent git processes); use targeted `git diff -- <path>` for specific files or `git ls-remote origin <ref>` to verify remote equality instead of attempting full status. Workaround applied: scoped path status + remote SHA verification in session_20260513_060550.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
