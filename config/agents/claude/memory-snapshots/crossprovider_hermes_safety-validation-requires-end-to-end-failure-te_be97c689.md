---
name: crossprovider hermes safety-validation-requires-end-to-end-failure-te
description: Safety validation requires end-to-end failure tests, not just unit tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, validation, safety, adversarial-review]
---

Unit tests of individual validation functions (e.g., `_scan_public_safe()`) can pass while end-to-end validation still accepts unsafe input because the caller only emits warnings instead of failing closed. Schema contracts claiming 'fails closed for unsafe paths' must have end-to-end tests verifying that any unsafe source causes validation to return an error, not just a warning count.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
