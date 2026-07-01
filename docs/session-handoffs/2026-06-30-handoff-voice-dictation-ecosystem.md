# Session Handoff — Voice Dictation Ecosystem Rollout

**Date:** 2026-06-30
**Branch:** `feat/voice-dictation-ecosystem` (2 commits, **NOT pushed** — see Blockers)
**Scope:** Free/local push-to-talk voice dictation across the machine ecosystem (RSI relief).

## What & why

User asked to "enable voice chat for Codex across all repos/machines" + voice across TigerVNC
to a second Linux box (`ace-linux-2`). Motivation: **elbow/finger pain (RSI)** across many OSes.

**Key finding:** Codex CLI (0.142.4) has **no native voice feature** — nothing to toggle. Solution =
a custom **free/local** STT layer: mic → `faster-whisper` (offline, no paid product) →
`xdotool`/`wtype` types into the focused window. Agent-agnostic (Codex, Claude Code, shell,
or an ssh/tmux pane to another machine).

## Delivered (branch `feat/voice-dictation-ecosystem`)

| Commit | Contents |
|--------|----------|
| `97a5e4b86` | `tools/voice-dictation/` (`codex-dictate.sh` toggle, `transcribe.py` STT, `dictate-test.sh`, `README.md`); `scripts/agents/install-voice-dictation.sh` (idempotent installer); `scripts/memory/bootstrap-machine.sh` §2.11 guarded hook |
| `1ee68f767` | Installer skips soundcard-less machines (detect via `/proc/asound/cards`; keep symlink, skip whisper+hotkey) |

**Per-OS strategy** (use each OS's best): Linux = this tool (`Super+Shift+V`, override via
`DICTATE_HOTKEY`); **macOS = native Fn/Globe twice**; **Windows = native Win+H**. Installer
no-ops with a reminder on Mac/Windows.

## Verified

- **`ace-linux-1` (X11, Plantronics headset):** mic→text confirmed (`HEARD: 'Testing the device now.'`),
  hotkey `Super+Shift+V` types into focused window, installer idempotent, symlink → repo (git pull auto-updates).
- **Gates:** `bash -n` + `py_compile`, `check-no-abs-paths.sh`, `shellcheck -S warning` — all clean.

## `ace-linux-2` (no sound card) — resolved as a non-issue

For dictation, the VNC **target** needs no sound card: dictate on `ace-linux-1` (has the mic),
`xdotool type` into the focused TigerVNC viewer → VNC forwards the **keystrokes (text, not audio)**
to `ace-linux-2`. Installer now detects soundcard-less machines and skips cleanly.

## Blockers / exceptions

1. **Push blocked (infra):** `git push` hangs non-interactively (~2 min timeout) — known push-auth
   blocker on this box. Branch is **local-only**; commits are the durable unit. Push must be run
   **interactively** by the user/operator.
2. **Auto-sync clobber:** a background `chore(sync)` moved the working checkout back to `main`
   mid-session and wiped working-tree files; the **branch ref + commits survived** and were restored.
   Reinforces: commit fast, remote branches are the only fully-safe state.
3. **Pre-existing dirty state on `main`:** auto-generated `*-dev-primary` state + `config/ai-tools/*`
   files were dirty on entry (self-healing equality/provider automation). **Not touched** — all commits
   used pathspec (`git commit -- <files>`) to avoid sweeping them.

## Next steps

1. **User/operator:** `git -C /mnt/local-analysis/workspace-hub push -u origin feat/voice-dictation-ecosystem`
   (interactive), then `gh pr create --repo vamseeachanta/workspace-hub --fill`.
2. On each other Linux machine: `git pull && bash scripts/memory/bootstrap-machine.sh`
   (+ one-time `sudo apt install alsa-utils xdotool`).
3. **Track B (PARKED, not built):** for working *on* `ace-linux-2`, VNC has no audio channel —
   don't bolt PipeWire-over-SSH onto TigerVNC. Use `ssh ace-linux-2` + `tmux` (most seamless, zero
   install) for agent/terminal work, or `xpra` (FOSS, audio over the same SSH) for a full desktop
   with sound. Writeup deferred to a follow-up session.

## No external actions taken

No emails/messages sent, no PRs opened, no pushes landed, no client-facing artifacts published.
Local changes only: files on `ace-linux-1` (symlinks in `~/.local/`, GNOME hotkey, `faster-whisper`
in miniforge python) + the local branch commits above.
