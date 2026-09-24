---
name: crossprovider gemini iso8601-date-parsing-handle-z-suffix-with-fromis
description: ISO8601 date parsing: handle Z-suffix with fromisoformat + replace
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [date-parsing, iso8601, timezone-handling]
---

Parse completed_at via datetime.fromisoformat(s.replace('Z', '+00:00')). fromisoformat doesn't natively handle Z notation; replace is needed.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
