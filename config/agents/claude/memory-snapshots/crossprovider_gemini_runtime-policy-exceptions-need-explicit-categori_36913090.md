---
name: crossprovider gemini runtime-policy-exceptions-need-explicit-categori
description: Runtime policy exceptions need explicit categorization
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [policy, scope-boundaries, documentation]
---

Policy work like 'always use uv run' must explicitly list allowed exceptions (e.g., interpreter discovery in `router.py`, bootstrap contexts, text-only mentions) so they're not counted as debt and implementation doesn't accidentally expand scope into pre-uv bootstrap code.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
