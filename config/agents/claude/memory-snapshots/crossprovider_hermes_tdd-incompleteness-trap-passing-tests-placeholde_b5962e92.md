---
name: crossprovider hermes tdd-incompleteness-trap-passing-tests-placeholde
description: TDD incompleteness trap: passing tests + placeholder implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, test-driven-development, implementation-validation, artifact-gates]
---

Agents on #2760 achieved passing test suites while implementation remained incomplete (missing DOCX output, placeholder OCIMF coefficients, generic trigonometry formulas). Artifact validation happened last, revealing gaps that unit tests missed. TDD requires explicit artifact-generation test cases, not just logic tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
