---
name: crossprovider codex shell-interpolation-breaks-gh-issue-comment-body
description: Shell interpolation breaks gh issue comment --body parameter when body contains backticks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gh-cli-quirk, shell-escaping, issue-comments]
---

Backticks and other special characters in issue comment bodies trigger shell interpolation when passed via `--body`. Workaround: use `gh issue comment --body-file <path>` to pass the body from a file, avoiding interpolation. This is a documented quirk of the gh CLI when orchestrating comments from subagent workflows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
