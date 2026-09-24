---
name: crossprovider codex silent-injection-of-defaults-during-schema-valid
description: Silent injection of defaults during schema validation hides malformed input
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, fail-closed, schema-design]
---

When validators supply default values for missing optional fields (e.g., `accepted_for_conversion: False` when absent), malformed or incomplete input passes validation instead of failing closed. Distinguish between fields that are truly optional and fields that must be present for validity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
