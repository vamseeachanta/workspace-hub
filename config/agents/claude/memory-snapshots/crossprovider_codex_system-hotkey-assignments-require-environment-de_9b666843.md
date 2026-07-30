---
name: crossprovider codex system-hotkey-assignments-require-environment-de
description: System hotkey assignments require environment detection and migration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [hotkeys, desktop-environments, collision-detection, user-experience]
---

Assigning a global hotkey like Super+H requires checking whether the desktop environment already reserves it. Ubuntu GNOME binds Super+H to minimize; assigning it for dictation without detecting and explicitly migrating that binding will minimize the app on key press. Design must detect session type (X11/Wayland), DE (GNOME/KDE), and existing gsettings bindings before assignment; document the required keybinding migration or choose a collision-free fallback.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
