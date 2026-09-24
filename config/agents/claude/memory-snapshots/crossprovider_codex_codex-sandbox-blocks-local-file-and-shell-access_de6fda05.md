---
name: crossprovider codex codex-sandbox-blocks-local-file-and-shell-access
description: Codex sandbox blocks local file and shell access; route verification to GitHub-native paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex-sandbox, plan-review, verification-pattern, workflow]
---

Codex sandbox cannot read local files or execute shell commands during plan review. When direct file access is blocked, verification must shift to GitHub API (for issue state, commits, diffs) and web-native reads (provider documentation, repo state via web UI). This is a converged workflow pattern from multiple plan reviews.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
