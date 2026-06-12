---
name: crossprovider hermes transactional-closeout-for-repo-structure-work
description: Transactional closeout for repo-structure work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflows, issue-closure, repo-structure]
---

Repo-structure issues must closeout in one session: validate test baseline, commit code, push, post GitHub comment, apply label cleanup, verify clean git status. Split across sessions leaves stale labels/dirty state that confuses future work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
