---
name: crossprovider gemini python-dict-access-in-session-logs-must-use-get-
description: Python dict access in session logs must use .get(), not attribute access
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python, json-parsing, error-handling]
---

Session log parsing yields Python dictionaries from `json.loads()`, not objects. Use `event.get('tool_name')` not `event.tool_name` to avoid AttributeError. Verify schema before assuming flat structure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
