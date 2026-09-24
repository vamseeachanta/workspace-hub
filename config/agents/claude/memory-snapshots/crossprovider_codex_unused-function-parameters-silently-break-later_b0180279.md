---
name: crossprovider codex unused-function-parameters-silently-break-later
description: Unused function parameters silently break later
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-design, correctness, detection-gap]
---

Accepting parameters in a function signature that are never used (e.g., W_in, H_in in flush_anode_resistance) creates an implicit contract where callers expect those parameters to affect behavior. Dead parameters are not caught by tests and lead to subtle defects when the function is refactored or when callers rely on the unused parameter.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
