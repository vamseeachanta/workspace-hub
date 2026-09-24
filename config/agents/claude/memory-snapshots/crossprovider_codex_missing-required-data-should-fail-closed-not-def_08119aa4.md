---
name: crossprovider codex missing-required-data-should-fail-closed-not-def
description: Missing required data should fail closed, not default empty
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [correctness, fail-closed, configuration]
---

When a required configuration is missing (e.g., `_load_private_lane_map(None)` returning `{}`), defaulting to empty state silently produces wrong results downstream. Fail explicitly and loudly so the problem surfaces before data corruption occurs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
