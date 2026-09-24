---
name: crossprovider codex documentation-implementation-consistency-is-a-hi
description: Documentation-implementation consistency is a high-frequency defect
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [documentation, specification-compliance, defect-pattern]
---

Claimed features in user-facing docs (e.g., 'Windows fallback available') often diverge from actual implementation constraints (e.g., `unsupported_platform` exception). Verify every user-facing claim against the implementation code and explicit error handling before marking docs as complete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
