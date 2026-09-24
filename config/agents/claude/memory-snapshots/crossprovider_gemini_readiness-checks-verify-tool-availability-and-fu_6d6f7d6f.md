---
name: crossprovider gemini readiness-checks-verify-tool-availability-and-fu
description: Readiness checks verify tool availability AND functionality
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [diagnostics, observability, ux]
---

Don't just check if tool is in PATH. Verify functionality with a quick test (e.g., 'uv run --no-project python -c "print(1)"'). Provide diagnostic commands on failure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
