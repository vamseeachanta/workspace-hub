---
name: crossprovider gemini optional-dependency-graceful-degradation
description: Optional dependency graceful degradation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell, dependencies, robustness]
---

Dependencies like setsid should degrade gracefully (warn and continue) rather than hard-fail. Check availability, warn if absent, set to empty string, and use conditionally in commands.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
