---
name: crossprovider hermes unmerged-branches-preserved-until-explicit-pr-cl
description: Unmerged branches preserved until explicit PR/close cycle
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [branch-hygiene, pr-workflow, preserved-branches]
---

After cleanup/pruning merged branches, preserve remaining 30+ unmerged branches (unique commits not in origin/main). PR/close them one-by-one: push to origin, create PR, verify checks, merge when green, clean up. Avoids destructive force-delete and ensures safe disposition of work-in-progress.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
