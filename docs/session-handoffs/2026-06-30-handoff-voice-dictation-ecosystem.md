# Voice Dictation Ecosystem Handoff

This historical handoff preserves the branch-only decision that #3403 restored:
dictation runs on the local Linux desktop that owns the microphone, then injects
typed text into whatever target has focus.

Operational contract:

- Local mic capture uses ALSA/`arecord`.
- Local STT uses `faster-whisper`.
- Text injection uses `xdotool`, `wtype`, or `ydotool`.
- VNC is treated as a display/keyboard surface only.
- Do not spend implementation time routing microphone audio through TigerVNC.

For remote terminal workflows, focus the SSH/tmux/VNC target and dictate from
the local desktop. The transcript becomes ordinary typed text in that target.
