---
name: crossprovider hermes dispatcher-agents-cannot-read-local-untracked-fi
description: Dispatcher agents cannot read local untracked files; push artifacts first
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [sandbox, dispatcher, git-boundary]
---

workspace-hub #2720 sessions show Codex/Hermes sandbox cannot access local `.planning/` or untracked files. Plan artifacts must be committed and pushed to GitHub BEFORE dispatching to agents for review or execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
