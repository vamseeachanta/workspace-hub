---
name: crossprovider hermes placeholder-test-implementations-pass-full-suite
description: Placeholder test implementations pass full suite but hide incomplete work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, tdd-antipattern, validation]
---

Tests using sentinel values like `OCIMF_CURRENT = 1.0` or hardcoded stubs pass completely, creating false confidence. Real verification requires: (1) replacing placeholders with live data access, (2) adding assertion tests for the data source itself, not just mock values.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
