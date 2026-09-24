---
name: crossprovider codex fail-before-i-o-is-security-critical-for-output-
description: Fail-before-I/O is security-critical for output validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, validation-order, design-pattern, fail-closed]
---

Output paths, provenance objects, and resource validation must execute before ANY database/I/O work. Late validation (after snapshot opens, queries run, or HMAC computed) violates fail-closed contracts and allows partial work on invalid inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
