---
name: crossprovider codex fail-fast-collision-detection-before-destructive
description: Fail-fast collision detection before destructive operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migrations, safety-pattern, data-loss-prevention]
---

Check for pre-existing target files before first apply. Fail immediately if targets exist, preventing overwrites. This is essential for migrations that copy source specs to centralized locations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
