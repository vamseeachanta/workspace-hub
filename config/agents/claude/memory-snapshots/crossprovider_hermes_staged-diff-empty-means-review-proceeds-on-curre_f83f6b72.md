---
name: crossprovider hermes staged-diff-empty-means-review-proceeds-on-curre
description: Staged diff empty means review proceeds on current tracked contents, not pending changes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, review-discovery, scope-clarification]
---

During #2521 OCIMF review, `git diff --cached` returned nothing; the session then reviewed current file contents rather than pending staged changes. This is a valid discovery pattern—file may already be committed or no changes staged—but shifts scope from staged patch to current state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
