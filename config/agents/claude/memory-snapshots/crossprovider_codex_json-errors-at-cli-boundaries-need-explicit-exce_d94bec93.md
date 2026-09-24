---
name: crossprovider codex json-errors-at-cli-boundaries-need-explicit-exce
description: JSON errors at CLI boundaries need explicit exception handling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, cli, json-parsing, exception-boundary]
---

AttributeError and TypeError from malformed JSON (e.g., `[]` or `null` as provenance mappings) escape generic exception handlers. Must catch these explicitly at CLI boundary alongside ValueError; don't rely on schema validation to catch structural mismatches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
