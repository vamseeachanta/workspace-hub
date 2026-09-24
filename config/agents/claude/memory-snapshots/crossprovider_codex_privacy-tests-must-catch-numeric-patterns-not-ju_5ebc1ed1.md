---
name: crossprovider codex privacy-tests-must-catch-numeric-patterns-not-ju
description: Privacy tests must catch numeric patterns, not just keyword strings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, testing, data-leakage, pattern-detection]
---

Banned-keyword searches ('timestamp', 'mtime') miss timestamp-like values embedded in filenames and extensions (e.g., `.2026-06-17.pdf`). Privacy regression tests need regex/heuristic pattern detection for numeric date-like strings, not just string containment checks, or they will pass while data still leaks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
