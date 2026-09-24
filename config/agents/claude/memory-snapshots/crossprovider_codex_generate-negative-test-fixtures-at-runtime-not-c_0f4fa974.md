---
name: crossprovider codex generate-negative-test-fixtures-at-runtime-not-c
description: Generate negative test fixtures at runtime, not committed files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, ci]
---

Generate negative fixture examples at runtime in temp files or fixture builders, never commit them to the repo. Prevents validators from blocking their own test artifacts and keeps the scanner/test boundary clean.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
