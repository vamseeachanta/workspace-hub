---
name: crossprovider codex private-evidence-cannot-be-tracked-in-public-sch
description: Private evidence cannot be tracked in public schema
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [privacy, schema-design, access-control]
---

Holdings, permissions, qualified-review evidence, and private validator dependencies cannot be represented in public repos. Validation tests that require private data need hermetic fixtures and explicit ownership contract with the private registry; otherwise defer the transition until the private schema exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
