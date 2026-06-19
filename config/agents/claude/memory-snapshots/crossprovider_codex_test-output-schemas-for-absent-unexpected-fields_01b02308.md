---
name: crossprovider codex test-output-schemas-for-absent-unexpected-fields
description: Test output schemas for absent unexpected fields, not just present expected ones
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [testing, schema, privacy]
---

Inherited output schemas may contain private-derived fields (e.g., `relative_path`, `filename`) even if the consuming code claims to filter them. Test that unexpected fields are absent from outputs, not just that expected fields exist; schema assertions alone don't prove downstream safety.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
