---
name: crossprovider codex gsettings-availability-requires-layered-checks-b
description: gsettings availability requires layered checks before mutation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [linux, gnome, d-bus, hotkeys]
---

D-Bus/DISPLAY/WAYLAND_DISPLAY may exist but gsettings may not be installed or the key may not be writable. Check command availability and writable status separately before gsettings set; store writable result in a variable before comparing to avoid compound conditional races.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
