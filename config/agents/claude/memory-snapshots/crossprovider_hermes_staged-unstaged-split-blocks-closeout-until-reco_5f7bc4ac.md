---
name: crossprovider hermes staged-unstaged-split-blocks-closeout-until-reco
description: Staged/unstaged split blocks closeout until reconciled
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, closeout-gate, index-safety]
---

When fixes span staged index and working tree, committing captures only staged state, leaving old bugs in the commit. Before closeout, reconcile all fixes into staged: use `git diff --cached` to verify the index contains the complete intended state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
