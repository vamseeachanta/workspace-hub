---
name: crossprovider codex enforcement-tool-test-files-cannot-contain-examp
description: Enforcement tool test files cannot contain examples of forbidden patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, self-blocking, test-design]
---

When a tool's test file contains committed-source examples of patterns the tool denies (negative test cases, deny-list samples, private identifier examples), tracking the test file makes the tool reject itself. This self-blocking circular dependency is specific to enforcement tools that scan source code. Negative examples must be runtime-generated, temporary, or use safe placeholders.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
