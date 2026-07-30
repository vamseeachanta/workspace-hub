---
name: crossprovider codex malformed-structured-fields-should-fail-validati
description: Malformed structured fields should fail validation, not silently inject defaults
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [data-validation, defensive-coding]
---

When a sidecar is missing optional fields like `accepted_for_conversion`, code injects `False` and validates the injected value instead of rejecting the malformed data. This hides stale/corrupted sidecars and prevents defensive fallback paths. Validate what you received, not what you invent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
