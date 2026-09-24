---
name: crossprovider codex commit-message-validation-from-logs-is-unreliabl
description: Commit-message validation from logs is unreliable — validate against git history or hook output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-validation, commit-messages, log-parsing]
---

Session logs truncate commit commands, making it impossible to reconstruct full commit messages. Codex reviews of WRK-691 flagged that a regex like `^(feat|fix|chore|...)\(` won't work on truncated logs and doesn't match the actual git-workflow hook rules (which allow `build`, `ci`, `merge`, `revert`, `wip`). Validate against git log or hook execution output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
