---
name: crossprovider codex prose-requirements-and-validator-implementations
description: Prose requirements and validator implementations diverge without test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, specification, validator, requirements]
---

A plan's written requirements (e.g., 'required fields must exist') do not automatically translate to validator enforcement. Tests must validate the actual implementation behavior, not just the intended spec. Gaps between prose and validator remain invisible until tests explicitly cover both.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
