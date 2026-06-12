---
name: crossprovider codex schema-declared-required-fields-must-match-verif
description: Schema-declared required fields must match verifier enforcement, or clearly distinguish schema-only vs enforced
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, verification, contract-clarity]
---

When a schema marks fields as required but verifier doesn't validate them, gates become fail-open. Either enforce all schema fields in the verifier, or explicitly label required-for-documentation vs validated. Mixing breaks agent trust when they follow schema but gates pass anyway.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
