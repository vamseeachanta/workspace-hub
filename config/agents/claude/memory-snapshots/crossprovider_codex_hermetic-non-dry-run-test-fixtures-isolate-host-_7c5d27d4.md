---
name: crossprovider codex hermetic-non-dry-run-test-fixtures-isolate-host-
description: Hermetic non-dry-run test fixtures isolate host interaction
metadata:
  type: reference
  source: codex
  bridged: 2026-07-13
  tags: [testing, hermetic, isolation, fixtures]
---

Test fixtures exercising actual (non-dry-run) behavior must isolate HOME and PATH, stub all reachable pre/post command libraries and auth scripts, record allowlisted system calls, and fail closed on unexpected host access. Prevents host-state pollution and catches unintended environmental dependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
