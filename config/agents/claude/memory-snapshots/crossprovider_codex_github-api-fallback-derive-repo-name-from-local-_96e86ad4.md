---
name: crossprovider codex github-api-fallback-derive-repo-name-from-local-
description: GitHub API fallback: derive repo name from local remotes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-connector, fallback-patterns]
---

When GitHub lookup returns 404 (connector unavailable or wrong repo name assumed), check `git remote -v` or `.git/config` to find the actual repository before attempting gate verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
