---
name: crossprovider codex system-capability-detection-actual-hardware-vs-c
description: System capability detection—actual hardware vs category existence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [voice-input, system-detection, robustness]
---

Sound card existence is insufficient for voice-input detection; must verify actual capture device availability (e.g., via `/proc/asound/cards`). Installers checking only for sound-card presence will silently fail on machines with HDMI-only audio or temporarily disconnected USB mics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
