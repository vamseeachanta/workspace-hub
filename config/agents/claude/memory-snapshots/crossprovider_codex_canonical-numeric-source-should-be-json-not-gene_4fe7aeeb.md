---
name: crossprovider codex canonical-numeric-source-should-be-json-not-gene
description: Canonical numeric source should be JSON, not generated markdown
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-format, artifact-management, code-generation]
---

When a script generates both machine-readable JSON and human-readable markdown from the same data, treat JSON as the source of truth. Markdown diverges over time through manual edits or stale regeneration; lock the approval contract on the JSON schema and require markdown regeneration through the script.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
