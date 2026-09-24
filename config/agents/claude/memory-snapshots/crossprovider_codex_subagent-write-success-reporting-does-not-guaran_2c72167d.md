---
name: crossprovider codex subagent-write-success-reporting-does-not-guaran
description: Subagent Write success reporting does not guarantee file landing; verify with ls
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subagent-behavior, verification, claude-code, tool-hazard]
---

Claude Code subagents can report Write tool success while the file does not actually land in the parent session's view (file cache freshness issue). Always verify critical file writes by running `ls` or `Read` in the main session after a subagent Write, especially when the next action depends on the file existing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
