---
name: crossprovider hermes branch-by-branch-pr-closure-must-verify-remote-s
description: Branch-by-branch PR closure must verify remote state before merge, not just PR creation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-pr-workflow, branch-hygiene, closure-pattern]
---

During preserved-branch PR sweeps, 'PR created' is not 'branch cleaned.' Only merge/delete after fresh `gh pr view` shows mergeable=true + required checks green. Stale GitHub API caches or pending CI can cause silent failures if you merge immediately after create.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
