---
name: crossprovider gemini hermetic-test-fixtures-outperform-live-feature-t
description: Hermetic test fixtures outperform live feature testing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, test-strategy, fixtures]
---

Integration tests against live WRK items are non-deterministic and mutate shared state. Tmp-dir fixtures with synthetic test data are isolated, repeatable, and safe. Allows full test coverage without polluting the live queue or requiring external coordination.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
