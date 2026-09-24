---
name: crossprovider codex codex-broker-write-sandbox-has-persistent-bwrap-
description: Codex broker-write sandbox has persistent bwrap errors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex-sandbox, shell-execution-blocked, environment-constraint]
---

Codex sandbox consistently fails with `bwrap: loopback: Failed RTM_NEWADDR` and `bwrap: setting up uid map: Permission denied`, blocking all local shell execution (gh, git, tests, Python). This is environmental, not code-related, and affects tasks requiring local git operations or test execution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
