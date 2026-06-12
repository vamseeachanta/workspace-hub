---
name: crossprovider hermes filesystem-enumeration-without-git-tracking-filt
description: Filesystem enumeration without git-tracking filters leaks draft/private content
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-scope, untracked-files, public-safety]
---

In #77, generator used wikis.rglob('*.md') without git ls-files filtering, so untracked pages under wikis/ were swept into public graph artifacts. Any 'committed' artifact contract must enumerate via git (git ls-files or git diff --cached) to exclude draft/private files that coexist in the worktree.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
