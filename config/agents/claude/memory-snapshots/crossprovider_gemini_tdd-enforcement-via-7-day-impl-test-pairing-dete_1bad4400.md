---
name: crossprovider gemini tdd-enforcement-via-7-day-impl-test-pairing-dete
description: TDD enforcement via 7-day impl-test pairing detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, tdd, quality-signals]
---

`test-health-check.sh` scans history, identifies impl files (py/ts/go/rs/etc) with no matching test file (test_*, *.test.*, *_test.*, *_spec.*). Emits per-repo pairing rate + unpaired list to JSONL signals. Surfaces TDD gaps without blocking.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
