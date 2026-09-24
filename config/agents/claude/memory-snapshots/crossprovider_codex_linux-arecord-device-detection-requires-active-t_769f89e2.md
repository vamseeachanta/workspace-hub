---
name: crossprovider codex linux-arecord-device-detection-requires-active-t
description: Linux arecord device detection requires active testing, not just /proc/asound/cards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [linux, audio, device-detection, voice-dictation]
---

Checking for sound card presence via `/proc/asound/cards` is insufficient. Systems can list HDMI or other cards there while `arecord default` still fails. Device selection must verify actual capture capability, not just presence inventory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
