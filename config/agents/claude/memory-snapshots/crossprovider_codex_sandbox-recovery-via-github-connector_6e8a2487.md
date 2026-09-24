---
name: crossprovider codex sandbox-recovery-via-github-connector
description: Sandbox recovery via GitHub connector
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, sandbox, fallback, github-api]
---

`bwrap: loopback` blocks local shell execution in Codex. Fall back to GitHub API for live inspection (issue state, archived repos, code reads). Accept that local-only evidence and artifact creation may be incomplete; cite connector as authoritative for GitHub state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
