---
name: crossprovider codex untracked-git-hooks-diverge-from-tracked-source
description: Untracked .git/hooks diverge from tracked source
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [enforcement, git-ops, version-control]
---

`.git/hooks/` is untracked and can diverge from its tracked source. Automated commits can delete the tracked hook file silently, and reinstalling the installer cannot restore it if the installer itself was the source of truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
