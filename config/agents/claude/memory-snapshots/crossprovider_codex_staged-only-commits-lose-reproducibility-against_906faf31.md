---
name: crossprovider codex staged-only-commits-lose-reproducibility-against
description: Staged-only commits lose reproducibility against reviewer tree
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [git, reproducibility, pr-hygiene, testing]
---

PRs staged but uncommitted in full can differ from what the reviewer sees. Always validate against full `git diff HEAD` including both staged and unstaged changes, not just `--cached`. Mixed staged/unstaged state creates a reproducibility risk — either commit fully or split into sequential PRs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
