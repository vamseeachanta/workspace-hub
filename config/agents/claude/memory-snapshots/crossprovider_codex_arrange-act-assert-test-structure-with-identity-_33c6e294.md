---
name: crossprovider codex arrange-act-assert-test-structure-with-identity-
description: Arrange-Act-Assert test structure with identity verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-structure, edge-cases]
---

Structure unit tests explicitly with Arrange (setup), Act (invoke), Assert (verify) phases. Test both behavior correctness and object identity (e.g., "result is not df" to verify copy semantics). Use tempfile for filesystem-touching tests to avoid test-order dependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
