---
name: crossprovider codex vnc-remote-desktop-dictation-via-keystroke-injec
description: VNC/remote desktop dictation via keystroke injection
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [voice-dictation, vnc, remote-desktop, architecture]
---

Do not route microphone audio through VNC; instead, run a local dictation service on the machine with the mic and inject keystrokes into the focused VNC window/viewer. This keeps consistent hotkey behavior (e.g. Super+Shift+V) across local terminals, Codex, Claude, and remote VNC targets without TigerVNC/PipeWire audio complexity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
