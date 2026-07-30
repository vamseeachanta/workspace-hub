---
name: crossprovider codex text-search-tests-false-green-when-behavior-fail
description: Text-search tests false-green when behavior fails
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [test-false-green, behavior-vs-text, test-design]
---

Test suites using grep/substring/regex verification can pass while the documented operation fails. A factory test checking that `template_commit` appears in logs passes even if the clone was never actually created with correct identity. Behavioral tests must exercise the full operation end-to-end, not just verify expected strings are present.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
