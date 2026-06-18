---
name: crossprovider codex generated-artifact-safety-needs-explicit-field-v
description: Generated-artifact safety needs explicit field/value restrictions
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [safety, schema, validation, licensing]
---

Content checks (marker scanning) catch strings but miss structural hazards: a schema allowing `licensed_content` field will pass marker checks but violate licensing rules. Use schema validation for allowed/forbidden field names alongside content checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
