---
name: crossprovider codex codex-bwrap-sandbox-loopback-permission-denied-o
description: Codex bwrap sandbox loopback permission denied on this machine
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex, sandbox, environment, blocker]
---

Multiple 2026-05-26 sessions failed with `bwrap: setting up uid map: Permission denied` and `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` when Codex attempted shell execution. This is a persistent sandbox environment constraint, not user error, blocking all local shell commands (git, gh, python, bash) in Codex runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
