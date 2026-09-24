---
name: crossprovider codex validate-sibling-repos-in-isolated-worktrees
description: Validate sibling repos in isolated worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-repo, validation, git-workflow]
---

When target implementation lives in a sibling repo (not the current checkout), fetch and validate in an isolated worktree rather than modifying local sibling checkouts that may have unrelated work. Keeps review isolation clean and avoids collisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
