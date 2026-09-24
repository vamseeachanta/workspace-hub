---
name: crossprovider codex required-contract-fields-need-negative-test-cove
description: Required contract fields need negative test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, contracts, schema]
---

Each field declared required should have explicit test cases that omit it and verify rejection; validating presence of supplied fields alone misses enforcement gaps. Discovered when tests passed but validators accepted rows with missing required fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
