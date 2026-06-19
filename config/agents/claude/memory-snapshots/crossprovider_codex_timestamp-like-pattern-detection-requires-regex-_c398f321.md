---
name: crossprovider codex timestamp-like-pattern-detection-requires-regex-
description: Timestamp-like pattern detection requires regex/pattern tests, not literal string checks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [testing-patterns, privacy-validation, test-completeness]
---

TDD that checks only for keywords 'timestamp' and 'mtime' missed numeric patterns like `20250805-204115`. Pattern-based tests (regex, date-format validation) are necessary alongside literal-string denials when timestamp-like values are forbidden in outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
