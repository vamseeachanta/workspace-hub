---
name: crossprovider gemini explicit-return-statements-in-stub-implementatio
description: Explicit return statements in stub implementations
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [stub-code, code-clarity, api-design]
---

Even no-op methods returning None should use explicit `return None` or `return result` statements. Implicit returns are ambiguous for future maintainers and hide the intent that the method may become non-trivial later.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
