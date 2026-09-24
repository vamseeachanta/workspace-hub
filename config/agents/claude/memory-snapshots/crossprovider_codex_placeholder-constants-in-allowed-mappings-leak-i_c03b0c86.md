---
name: crossprovider codex placeholder-constants-in-allowed-mappings-leak-i
description: Placeholder constants in allowed mappings leak into generated output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, production-safety, validation]
---

Placeholder constants like `required-new-source-family-issue` in ALLOWED_CLASSES will appear in generated artifact outputs if they match any valid input row, even if unused in a particular batch. Remove the placeholder class entirely from production mappings rather than keeping it as dead code; dead code in allowlists is not safe.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
