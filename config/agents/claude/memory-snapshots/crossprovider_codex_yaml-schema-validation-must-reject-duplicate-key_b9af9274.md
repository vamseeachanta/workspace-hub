---
name: crossprovider codex yaml-schema-validation-must-reject-duplicate-key
description: YAML schema validation must reject duplicate keys and validate scalar types exactly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [yaml-validation, schema-strictness, configuration-safety, defect-class]
---

yaml.safe_load() silently accepts duplicate mapping keys using last-value-wins semantics and treats type equality (e.g., schema_version: true == 1 in Python). Configuration/manifest validation requires a duplicate-key-rejecting SafeLoader subclass and exact type checks (type(x) is int, not ==); equality checks alone allow malformed manifests to be accepted and silently disable required fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
