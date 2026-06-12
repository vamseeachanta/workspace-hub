---
name: crossprovider hermes validators-pass-incomplete-implementations-of-ac
description: Validators pass incomplete implementations of acceptance criteria
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, acceptance-criteria, validator-patterns]
---

llm-wiki #75: tests pass; validator passes; but acceptance-critical features (baseline/delta computation, JSON companion requirement) are unimplemented. Schema-level validation doesn't catch missing feature logic. Tests must verify acceptance criteria end-to-end, not schema/syntax alone.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
