---
name: crossprovider codex data-leakage-escapes-tdd-via-generated-output
description: Data-leakage escapes TDD via generated output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-gaps, runtime-behavior, adversarial-review]
---

Timestamp-like filename fragments leaked into JSON extension_mix field despite unit tests passing. Tests exercised specific fixtures; runtime walked real filesystem. Adversarial review must regenerate outputs against live source and scan actual artifacts, not trust fixture-based test results alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
