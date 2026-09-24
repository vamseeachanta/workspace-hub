---
name: crossprovider gemini non-claude-agents-need-harness-directive-files-t
description: Non-Claude agents need harness-directive files to mandate wrapper usage
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [agent-infrastructure, multi-provider, gate-contract]
---

Codex and Gemini agents require workspace-root files (CODEX.md, GEMINI.md, ≤20 lines) that mandate using `/work run` wrappers (session.sh → work.sh → execute.sh, etc.). Direct provider calls bypass wrapper logging and are detectable via missing log entries. Without these directives, agents have no guidance to use the centralized gate infrastructure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
