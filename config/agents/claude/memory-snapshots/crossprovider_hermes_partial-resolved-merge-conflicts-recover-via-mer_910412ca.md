---
name: crossprovider hermes partial-resolved-merge-conflicts-recover-via-mer
description: Partial-resolved merge conflicts recover via merge --continue
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [merge-conflict, recovery, git-flow]
---

After `git merge --abort` during a conflict, manual inspection can inform a retry. If the conflict is partially resolvable (e.g., keeping one side with `git checkout --ours`), use `git merge --continue` to complete rather than aborting and retrying the full merge.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
