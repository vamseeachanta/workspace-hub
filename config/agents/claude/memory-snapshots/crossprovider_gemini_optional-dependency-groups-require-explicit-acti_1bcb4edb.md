---
name: crossprovider gemini optional-dependency-groups-require-explicit-acti
description: Optional dependency groups require explicit activation in uv run
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [dependency-management, uv, python]
---

Script using dependency from `[dependency-groups].optional-dev` silently fails (ModuleNotFoundError) unless activated. Either use `uv run --with <group>` or ensure group is in default activation set. Verify activation in test.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
