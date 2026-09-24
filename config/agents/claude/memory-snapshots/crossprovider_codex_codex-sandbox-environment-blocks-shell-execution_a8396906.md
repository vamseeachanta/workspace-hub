---
name: crossprovider codex codex-sandbox-environment-blocks-shell-execution
description: Codex sandbox environment blocks shell execution; fallback via GitHub API
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment, sandbox, codex-agent, fallback-verification]
---

The Codex agent in this workspace environment runs under strict `bwrap` sandboxing that blocks shell spawning, process execution, and occasionally file writes (`bwrap: loopback: Failed RTM_NEWADDR`). Verified claims via GitHub repository blob API and filesystem reads instead when shell fails; this should be the documented fallback path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
