---
name: crossprovider codex approval-gate-schema-must-be-explicit-path-forma
description: Approval gate schema must be explicit (path, format, validator) or it remains unenforceable
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [approval-gate, governance, validation]
---

Plans claiming approval markers (e.g., 'require local marker in addition to GitHub label') must define marker file path, YAML/JSON schema, and deterministic validator function in the plan itself. Without it, downstream validators cannot be written. GitHub labels alone are insufficient if plan logic requires offline markers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
