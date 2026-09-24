---
name: crossprovider codex read-only-ancestry-audit-before-merge-vs-rebase-
description: Read-only ancestry audit before merge-vs-rebase decision
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, pre-merge-checklist, branch-safety]
---

Before deciding whether to merge or rebase a feature branch, verify: (1) PR merge-commit is ancestor of feature HEAD, (2) current commit divergence (left/right counts), (3) path overlap and textual conflicts via merge-tree, (4) upstream configuration accuracy. Document force-push hazards upfront; prefer merge if branch is already published.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
