---
name: crossprovider hermes minimal-procedural-helper-modules-for-test-code-
description: Minimal procedural helper modules for test code deduplication
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-organization, testing, helpers]
---

When tests duplicate pattern lists and scanning logic, create a procedural helper module (no classes) exporting a tuple type and single scan function. Keep test assertions and file lists local so tests remain readable and independent.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
