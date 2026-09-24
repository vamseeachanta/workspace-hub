---
name: crossprovider codex subagent-write-success-claims-require-main-sessi
description: Subagent Write success claims require main-session verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subagents, file-operations, verification]
---

Subagents can report Write tool success while files do not actually persist (filesystem delays, permission issues, etc.). After subagent completion, main session must `ls` to verify files exist before trusting the artifact.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
