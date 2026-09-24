---
name: crossprovider codex output-only-leakage-tests-cannot-verify-forbidde
description: Output-only leakage tests cannot verify forbidden operations; add operation-level checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, security, leakage-detection, test-design]
---

A test that forbids copying source text can pass while the implementation still reads raw source files (then paraphrases). Add tests that fail on attempts to resolve/open source paths, not just on output content. Boundary-level checks (no resolver calls, no file opens) catch intent violations output tests miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
