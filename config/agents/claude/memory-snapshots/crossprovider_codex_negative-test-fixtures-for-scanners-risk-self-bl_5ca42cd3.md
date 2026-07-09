---
name: crossprovider codex negative-test-fixtures-for-scanners-risk-self-bl
description: Negative test fixtures for scanners risk self-blocking if stored in scanned directories
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [testing, scanner-hazards, test-isolation]
---

Writing test cases with intentionally-denied patterns (raw paths, forbidden keys, etc.) in a test file often causes the scanner to reject its own test fixtures. Pattern: store negative fixtures in a separate directory with explicit baseline/exemption rules, or mark fixtures with a sentinel comment ('# transport-path-allowed') that scanner regex exempts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
