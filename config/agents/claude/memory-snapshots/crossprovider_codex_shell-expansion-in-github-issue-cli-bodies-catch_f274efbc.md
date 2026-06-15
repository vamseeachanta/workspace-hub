---
name: crossprovider codex shell-expansion-in-github-issue-cli-bodies-catch
description: Shell expansion in GitHub issue CLI bodies; catch by re-reading post-creation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [tooling, github-cli]
---

When creating issues via `gh` with backtick-delimited paths in the body, the shell expands them before posting. Fix by re-reading issue bodies after creation and correcting garbled paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
