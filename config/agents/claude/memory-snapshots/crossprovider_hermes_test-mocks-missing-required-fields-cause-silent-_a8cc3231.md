---
name: crossprovider hermes test-mocks-missing-required-fields-cause-silent-
description: Test mocks missing required fields cause silent test failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, mocks, test-driven-development]
---

Index record tests with partial mocks (missing doc_path) silently passed; field-dependency bugs undetected. Always include full required field sets in mocks; use dataclass validation or factory functions to enforce completeness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
