---
name: crossprovider codex nested-jsonl-envelope-extraction-requires-null-s
description: Nested JSONL envelope extraction requires null-safe traversal
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [agent-integration, jsonl, data-extraction, envelope-format]
---

Agent session logs require chained JSON parsing (response_item → function_call → exec_command → arguments). Each level can be absent or present; double-parsing required. Callers must handle missing intermediate objects without crashing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
