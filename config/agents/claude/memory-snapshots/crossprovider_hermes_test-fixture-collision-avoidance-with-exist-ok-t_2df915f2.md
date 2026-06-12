---
name: crossprovider hermes test-fixture-collision-avoidance-with-exist-ok-t
description: Test fixture collision avoidance with exist_ok=True
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, fixtures, idempotency]
---

When test fixtures create shared directories (e.g., .git for multiple test runs), use `mkdir(exist_ok=True)` or path-unique fixtures to prevent collision. A fixture creating the same workspace path multiple times fails if the first run doesn't clean up.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
