---
name: crossprovider codex multi-step-shell-mutations-commit-tag-update-nee
description: Multi-step shell mutations (commit→tag→update) need atomic/rollback
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-patterns, release-automation, atomicity, git]
---

Release scripts that sequence git mutations (commit, tag, push) can leave repos in partial state if a middle step fails. Either collect all mutations and apply atomically, or wrap sequence in guard with rollback on error. Seen in release-manifest updates where submodule commits before hub metadata update.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
