---
name: crossprovider hermes github-issue-markdown-paths-must-use-body-file-n
description: GitHub issue Markdown/paths must use --body-file, not inline --body
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-cli, tool-quirk]
---

Inline `--body` with Markdown, backticks, paths, or dynamic content fails silently or truncates. Always use `--body-file <path>` for issue bodies and plan comments containing structured content, code blocks, or file paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
