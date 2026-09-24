---
name: crossprovider codex import-level-test-assertions-must-not-forbid-opt
description: Import-level test assertions must not forbid optional imports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-antipattern, optional-dependencies, import-guards]
---

When a test forbids all import attempts for an optional dependency (even if caught and handled), the test overconstrains compliant code that uses optional-import probes for feature detection. Test 'no hard dependency required,' not 'no import attempt whatsoever.'

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
