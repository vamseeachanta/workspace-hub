---
name: crossprovider codex installer-mic-detection-verify-capture-device-no
description: Installer mic detection: verify capture device, not just sound card presence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [installer, audio-detection, robustness, device-discovery]
---

Checking for 'any sound card' misses the actual requirement—a box with HDMI audio output but no capture device will falsely appear capable. Better check: verify capture hardware is present (`arecord -l` or `/proc/asound/cards`) before activating the hotkey. Prevent the hotkey from running an inert no-op when mic is absent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
