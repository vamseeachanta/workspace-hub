---
name: crossprovider hermes gh-issue-create-markdown-backticks-paths-require
description: gh issue create: markdown/backticks/paths require --body-file, not inline --body
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gh-cli, github-api, tooling]
---

`gh issue create --body` with inline markdown, backticks, file paths, or dynamic content loses formatting or fails parsing; use `--body-file <path>` to preserve structure. Also applies to `gh issue comment --body-file`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
