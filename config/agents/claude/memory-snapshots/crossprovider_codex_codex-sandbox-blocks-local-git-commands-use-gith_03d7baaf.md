---
name: crossprovider codex codex-sandbox-blocks-local-git-commands-use-gith
description: Codex sandbox blocks local git commands; use GitHub MCP for remote verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex-environment, sandbox-limitation, git-verification]
---

Codex encounters persistent `bwrap: loopback: Failed RTM_NEWADDR` errors when running `git show` or `git ls-files` locally. For artifact/commit verification during reviews, pivot to GitHub MCP repo connector to fetch file contents and blob metadata remotely instead of relying on local shell commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
