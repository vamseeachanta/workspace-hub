---
name: crossprovider codex validation-boundaries-must-enforce-safety-for-li
description: Validation boundaries must enforce safety for library reuse, not just CLI
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, api-design, reusability]
---

If a builder function is called both from CLI (with validation) and imported as a library, the validation must be in the function signature itself. Otherwise, programmatic callers bypass safety guards. Apply _validate_output() inside the builder, not just at main().

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
