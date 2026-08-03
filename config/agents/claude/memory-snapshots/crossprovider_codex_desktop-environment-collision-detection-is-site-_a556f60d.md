---
name: crossprovider codex desktop-environment-collision-detection-is-site-
description: Desktop environment collision detection is site-specific, needs explicit fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [environment, collision-detection, design]
---

System shortcuts vary by environment (GNOME reserves Super+H for minimize). Design must detect collisions and document migration/rollback. Shortcut parity across OS (Windows Win+H, Linux Super+H) requires explicit collision handling per desktop, not a single binding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
