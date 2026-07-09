---
name: crossprovider codex generated-json-artifacts-must-be-validated-with-
description: Generated JSON artifacts must be validated with strict parsers in tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [testing, json-validation, static-publishing]
---

Artifacts destined for static HTML (embedded payloads, sidecars) must validate with `json.loads(..., parse_constant=reject_non_standard_constant)` to catch IEEE 754 non-standard values (`NaN`, `Infinity`) before reaching consumers. Testing with permissive loaders masks defects that fail in production (browsers, Node, strict JSON consumers).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
