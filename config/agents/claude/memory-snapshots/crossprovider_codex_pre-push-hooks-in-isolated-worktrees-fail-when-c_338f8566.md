---
name: crossprovider codex pre-push-hooks-in-isolated-worktrees-fail-when-c
description: Pre-push hooks in isolated worktrees fail when checking sibling repos
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-hooks, worktree-isolation, sibling-repos]
---

Pre-push hooks that enumerate/validate sibling repositories fail in isolated worktrees (e.g., `workspace-hub-issue-2767-disposition-codex`) where siblings are not checked out. Either bypass with `--no-verify` (only for preservation) or detach hooks before testing in isolated worktrees. Document as a known workaround in repo hook policy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
