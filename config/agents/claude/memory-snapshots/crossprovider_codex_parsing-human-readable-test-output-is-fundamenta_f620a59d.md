---
name: crossprovider codex parsing-human-readable-test-output-is-fundamenta
description: Parsing human-readable test output is fundamentally brittle—use structured formats with exit-code fallbacks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest-automation, test-parsing, structured-output, WRK-1054]
---

Parsing pytest summary lines (e.g., 'X passed, Y failed') fails silently on collection/import errors, timeouts, interrupted runs, and plugin-driven aborts that don't emit a normal summary. Always use structured output (JUnit XML, JSON report) for machine parsing and treat pytest exit code as the primary control signal. Fallback to exit code when no parseable summary exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
