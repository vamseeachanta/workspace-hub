---
name: crossprovider codex parallel-work-in-shared-checkouts-requires-expli
description: Parallel work in shared checkouts requires explicit cross-machine claim labels and rebase residue awareness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-operations, parallel-work, repository-state]
---

Use `wip:*` labels to claim machines and coordinate parallel sessions; skip any issue carrying such a label until removed. Git rebase residue (`.git/rebase-merge`) persists after rebase completion/failure and requires manual cleanup—check for and clean it explicitly. Multiple processes can race on the same checkout; verify lock/rebase state before writing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
