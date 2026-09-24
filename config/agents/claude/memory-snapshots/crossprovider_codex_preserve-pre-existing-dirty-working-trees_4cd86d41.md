---
name: crossprovider codex preserve-pre-existing-dirty-working-trees
description: Preserve pre-existing dirty working trees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, safety, user-state]
---

When a repo clone has untracked local state (notes, scratch files), preserve it rather than merge-cleaning. The user may have in-progress work. Use lower-I/O update paths (e.g., partial clone, fetch instead of full checkout) to avoid disturbing the working tree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
