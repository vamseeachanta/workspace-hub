---
name: crossprovider codex bootstrap-gitattributes-before-merging-new-branc
description: Bootstrap .gitattributes before merging new branches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-merge, gitattributes, union-driver, procedure]
---

When a branch lacks .gitattributes, bring it from main first with `git checkout origin/main -- .gitattributes && git commit` before merging so the union driver is active. Without this bootstrap, merge conflicts appear on append-only files that should auto-resolve.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
