---
name: crossprovider codex subagent-main-session-isolation-main-must-verify
description: Subagent-main session isolation: main must verify success claims before trusting subagent work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subagents, verification, isolation]
---

Subagents run with fresh context and cannot see main conversation. A subagent report of Write success does not guarantee the file landed (phantom-write hazard). Main session must verify via `ls`, `git status`, or Read before relying on subagent claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
