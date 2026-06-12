---
name: crossprovider gemini session-log-schemas-are-nested-not-flat-event-at
description: Session log schemas are nested, not flat; event attributes are not top-level
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-structure, schema, session-logs]
---

Plans assume `event.tool_name` and `event.ts` as direct attributes, but actual session logs have nested structure. Dictionary access must use `.get()` with proper nesting. Schema assumptions must be verified against source code, not guessed from sampled files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
