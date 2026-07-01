---
name: crossprovider codex marker-format-documentation-code-mismatch-silent
description: Marker format documentation-code mismatch silently fails validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [documentation-sync, schema-evolution, test-coverage]
---

Documented marker format (bullet-list values under headers) can be rejected by validator code expecting inline values. Validators and documentation must be validated together in test fixtures; test both documented and actual formats.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
