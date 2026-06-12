---
name: crossprovider hermes helper-fallback-must-test-execution-not-just-com
description: Helper fallback must test execution not just command presence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell, error-handling, fallbacks, anti-pattern]
---

Choosing python3 via `command -v python3` check does not guarantee execution works. Helpers that prefer python3 but should fallback to uv fail when python3 exists but is broken. Pattern: test execution result, not just command presence; fail gracefully and try next alternative.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
