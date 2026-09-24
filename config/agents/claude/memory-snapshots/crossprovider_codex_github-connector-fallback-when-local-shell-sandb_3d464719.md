---
name: crossprovider codex github-connector-fallback-when-local-shell-sandb
description: GitHub connector fallback when local shell sandbox fails
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operational, sandboxing, github-connector, subagent-resilience]
---

When `bwrap` sandbox blocks local command execution (`Failed RTM_NEWADDR`), GitHub connector remains functional for reading issues, PR metadata, and public repo files. Audits and reviews can proceed read-only via GitHub APIs instead of abandoning work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
