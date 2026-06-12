---
name: crossprovider hermes post-reboot-git-recovery-identify-active-writers
description: Post-reboot git recovery: identify active writers before mutations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-recovery, post-reboot, workspace-management]
---

After reboot, stale `.git/index.lock` exists but is safe to remove only if unowned. Before any git state mutations (reset/rebase), confirm no interactive Claude/Hermes/Codex writers remain via process inventory. Write salvage diffs to `/mnt/local-analysis/reboot-salvage-TIMESTAMP/` BEFORE attempting rebase. Rebase safely onto origin/main without force-push; verify owned files in the commit before closeout/GitHub comment.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
