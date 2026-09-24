---
name: crossprovider codex marker-based-test-exclusion-expected-failures-in
description: Marker-based test exclusion + expected-failures interaction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, testing, ci-patterns]
---

When a flag re-selects pytest-marked tests (e.g., `--include-live`), must also remove those tests from the expected-failures list, or the flag becomes cosmetic and masks actual failures. Re-selection requires removing suppression.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
