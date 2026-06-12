---
name: crossprovider codex worktree-dirty-state-should-be-isolated
description: Worktree dirty state should be isolated
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [worktree-discipline, scope-isolation, commit-safety]
---

When working on issue-scoped ingests, document and isolate edits to specific domain paths (e.g., wikis/engineering-standards/). Leave unrelated worktree changes (acma, .codex, .gemini) untouched. Prevents silent commits of out-of-scope work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
