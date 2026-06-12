---
name: crossprovider codex tdd-claims-require-tests-defined-before-artifact
description: TDD claims require tests defined before artifacts, not after
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tdd, testing, plan-verification]
---

Plans claiming TDD compliance but describing "Author artifact X, then validate..." are implementation-first. True TDD requires tests/validators to be defined in the plan before the artifacts they validate. The sequence matters.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
