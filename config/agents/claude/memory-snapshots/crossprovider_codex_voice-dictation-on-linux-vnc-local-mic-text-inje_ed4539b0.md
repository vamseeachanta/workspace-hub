---
name: crossprovider codex voice-dictation-on-linux-vnc-local-mic-text-inje
description: Voice dictation on Linux+VNC: local mic + text injection, not audio forwarding
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [voice-dictation, linux, vnc, audio, text-injection]
---

Do not route microphone audio through VNC. Capture on the machine with the physical mic, then inject typed text into whatever window has focus via xdotool/wtype. This single pattern works for local terminals, remote SSH, and VNC viewers without audio-routing complexity. Uses ALSA/arecord for capture, faster-whisper for STT, and X text injection for input.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
