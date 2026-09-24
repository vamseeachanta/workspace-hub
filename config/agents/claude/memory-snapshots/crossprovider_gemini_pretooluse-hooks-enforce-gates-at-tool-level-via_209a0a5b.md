---
name: crossprovider gemini pretooluse-hooks-enforce-gates-at-tool-level-via
description: PreToolUse hooks enforce gates at tool level via YAML state files
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gates, tool-hooks, enforcement]
---

gate-check.py model: hooks intercept Write tool calls and check YAML decision/confirmed_by fields before allowing writes to gated artifacts. Moves gate enforcement from process discipline to tool-level enforcement, unbypassable by agents.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
