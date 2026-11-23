# Voice Dictation

Linux push-to-talk dictation for the focused text box. The local machine records
the microphone with `arecord`, transcribes with `faster-whisper`, and injects
plain text through `xdotool`, `wtype`, or `ydotool`.

The persistent install path is:

```bash
bash scripts/agents/install-voice-dictation.sh
```

On a GNOME desktop with a working capture device and a Python interpreter that
can import `faster_whisper`, the installer binds `Super+Shift+V` to
`~/.local/share/voice-dictation/codex-dictate.sh`. The command stores a concrete
ALSA device such as `plughw:1,0`, so it survives broken `default` ALSA routing.
Re-run the installer after changing USB microphones to refresh the stored
device. Run the installer from the primary checkout after the change is on
`main`; linked worktrees are resolved to the primary checkout when possible so
the hotkey does not point at a disposable worktree path.

Use this workflow for VNC:

- Dictate on the machine that has the microphone.
- Put focus in the VNC, SSH, tmux, browser, Codex, or Claude text box.
- Press `Super+Shift+V`; the transcript is typed into the focused target.

Do not route microphone audio through TigerVNC for this workflow. VNC is only the
remote display/input surface; dictation remains local and sends typed text.

Useful checks:

```bash
bash scripts/agents/lib/voice-dictation-detect.sh --choose
~/.local/share/voice-dictation/dictate-test.sh 5 "$(bash scripts/agents/lib/voice-dictation-detect.sh --choose)"
```

If no text injector is installed, transcription still prints to stdout. Install
`xdotool` for X11 or `wtype`/`ydotool` for Wayland to type automatically.

Runtime files live in `XDG_RUNTIME_DIR/codex-dictate` when available, otherwise
in a private `700` fallback directory under `${TMPDIR:-/tmp}` named
`codex-dictate-$(id -u)`. Set `DICTATE_MODEL`, `DICTATE_DEVICE`,
`DICTATE_COMPUTE`, or `DICTATE_LANGUAGE` to override the default
`faster-whisper` settings.
