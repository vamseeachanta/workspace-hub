# voice-dictation — free/local push-to-talk for the whole ecosystem

Talk, and it types into whatever window has focus — Codex, Claude Code, a
shell, or an SSH/tmux pane to another machine. **100% free and offline**: no
paid product, no cloud API, no per-token cost. Built for RSI relief across many
machines and operating systems.

## Per-OS strategy (use the best tool each OS already has)

| OS | What you press | How it's provided |
|----|----------------|-------------------|
| **Linux** | `Super + Shift + V` (default) | This tool — `arecord` → `faster-whisper` → `xdotool`/`wtype` |
| **macOS** | **Fn / Globe key, twice** | Built-in macOS Dictation (no install) |
| **Windows** | **`Win + H`** | Built-in Windows Voice Typing (no install) |

Linux has no built-in dictation, so we ship one. macOS and Windows already do it
well offline — `install-voice-dictation.sh` just prints the reminder there.

## Install

Automatic on every machine via `scripts/memory/bootstrap-machine.sh`. Manual:

```bash
bash scripts/agents/install-voice-dictation.sh
```

On Linux it symlinks this folder to `~/.local/share/voice-dictation` (so
`git pull` updates it), ensures a Python with `faster-whisper`, reports any
missing system packages, and binds the GNOME hotkey.

### System dependencies (Linux, user installs once)

```bash
sudo apt install -y alsa-utils xdotool      # X11
sudo apt install -y alsa-utils wtype        # Wayland
```

`faster-whisper` is installed into your Python automatically (user-space, no sudo).

## Use

1. Focus any text field.
2. Press the hotkey → "🎙 recording…" — **speak**.
3. Press it again → "transcribing…" → your words type themselves in.

## Test without binding a key

```bash
~/.local/share/voice-dictation/dictate-test.sh        # records 5s, prints what it heard
~/.local/share/voice-dictation/dictate-test.sh 8 plughw:1,0   # 8s, specific mic
```

## Tunables (env)

| Var | Default | Purpose |
|-----|---------|---------|
| `DICTATE_HOTKEY` | `<Super><Shift>v` | GNOME binding (set before install) |
| `DICTATE_PYTHON` | autodetected | Force the interpreter that has faster-whisper |
| `DICTATE_DEVICE_ALSA` | `default` | `arecord -D` target (e.g. `plughw:1,0`) |
| `DICTATE_MODEL` | `base.en` | Whisper size: `tiny.en` faster, `small.en` more accurate |
| `DICTATE_DEVICE` / `DICTATE_COMPUTE` | `cpu` / `int8` | Set `cuda` / `float16` on a GPU box |

## Files

- `codex-dictate.sh` — the push-to-talk toggle (bind this to a hotkey)
- `transcribe.py` — local faster-whisper STT (WAV → text on stdout)
- `dictate-test.sh` — fixed-duration mic/STT check (prints, doesn't type)

## Notes

- **Wayland** keystroke injection needs `wtype` (or a running `ydotool` daemon);
  the toggle auto-selects it when `WAYLAND_DISPLAY` is set.
- `vad_filter` in `transcribe.py` suppresses Whisper's phantom text on silence.
- For working *on another machine*, dictate into an `ssh <host>` + `tmux` pane —
  the text injects locally into the focused terminal, no remote setup needed.
