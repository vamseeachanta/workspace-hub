# Session handoff — vnc-ace-linux-2.sh headless-first fix

> **Date:** 2026-07-18 · **Lane:** lane:claude (interactive) · **Status:** ✅ COMPLETE — user-verified working ("it worked")

## Symptom

`bash scripts/operations/connection/vnc-ace-linux-2.sh` failed with
`UNREACHABLE display=:0` / "is anyone logged into the desktop?" — ace-linux-2 is
headless, so the script's only path (x11vnc mirroring the physical `:0`) could
never work without a graphical login.

## Root causes (three, stacked)

1. **Script had no headless path.** The always-on headless TigerVNC virtual
   desktop (`tigervncserver@:1.service`, `Xtigervnc` on `127.0.0.1:5901`,
   `SecurityTypes=None` + localhost-only, GNOME via `~/.vnc/xstartup`) was
   healthy the whole time — the script simply never looked at it.
2. **A prior fix never landed.** Auto-memory recorded a 2026-07-02 rewrite of
   this script to use `:1/5901`, but `origin/main` still carried the x11vnc
   version — the rewrite evidently existed only on a working copy and was lost.
   (Same durability theme as the NTFS-FUSE exec-bit losses — see #3577.)
3. **Duplicate flapping unit.** A USER systemd unit `vncserver@:1.service` was
   stuck in `activating auto-restart` against the display already owned by the
   SYSTEM unit.

## Fix (all landed)

- **Script rewritten headless-first** — commit `1b3b7ed24` on `main`
  (mode 100755): default = tunnel `5900→localhost:5901` to the headless `:1`
  (works with zero logins); `--mirror` = previous x11vnc-on-`:0` behavior
  (explicit opt-in + automatic fallback when `:1` is down).
- **Box cleanup (applied live on ace-linux-2):** user unit `vncserver@:1`
  disabled + stopped; system `tigervncserver@:1.service` remains
  active + enabled (reboot-safe).
- **Canonical FUSE working copy synced** to the pushed content so the script
  worked immediately (no drift vs `origin/main`).
- **Auto-memory corrected:** `reference_ace_linux_2_headless_vnc` now records
  the landed commit and the box cleanup.

## Verification

- Agent: SSH probe showed `Xtigervnc` listening on `127.0.0.1:5901`; live SSH
  tunnel completed the VNC handshake (`RFB 003.008` banner read through the
  tunnel).
- User: ran the script, viewer opened the headless desktop — confirmed working.

## State at exit

- `origin/main` carries the fix; no branches, PRs, or background processes left
  behind (test tunnel was self-expiring).
- No open follow-ups from this task. The durability lesson (working-copy edits
  that never reach the remote) is already covered by #3577's exec-bit/NTFS-FUSE
  sweep context.
