---
name: crossprovider gemini explicit-exception-categories-prevent-policy-dri
description: Explicit exception categories prevent policy drift
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [policy-enforcement, code-standards, documentation]
---

When defining enforcement rules (e.g., 'never bare python3'), name the exception categories explicitly (interpreter-discovery, pre-uv bootstrap, text-only mentions) and require code comments for instances. Implicit exceptions accumulate silently into violations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
