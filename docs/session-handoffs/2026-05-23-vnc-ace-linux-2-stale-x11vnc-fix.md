# Session Handoff — VNC connect helper: stale x11vnc fix (ace-linux-2)

- **Date:** 2026-05-23
- **Machine:** ace-linux-1 (operator) → ace-linux-2 (VNC target)
- **Scope:** Fix `scripts/operations/connection/vnc-ace-linux-2.sh` failing to display a desktop.
- **Status:** DONE, committed to `main`, verified live.

## Problem

Running the VNC helper connected at the RFB layer but the viewer immediately
logged `End of stream` / `DecodeManager: 0 rects, 0 pixels` and the tunnel
closed — a black/dead session.

## Root cause

Two defects in the helper, one active and one latent:

1. **Active failure — zombie reuse.** A 26-day-old `x11vnc` (pid 139692, started
   Apr27, ~3464 min CPU) was bound to `:5900` but its X connection had gone stale
   after the GNOME/Wayland session restarted underneath it. It accepted the
   viewer, completed the RFB handshake, then served zero frames. The helper's
   health check was `ss | grep :5900` — a *port-bound* test, not a *liveness*
   test — so it happily reused the zombie.
2. **Latent failure — Wayland-blind auth.** The auto-start path discovered the X
   auth file by grepping for a `/usr/lib/xorg/Xorg` process. `ace-linux-2` runs
   GNOME/**Wayland** — no `Xorg` process exists; auth lives at
   `/run/user/1000/gdm/Xauthority`. So even with a free port, auto-start would
   have failed to find auth.

The display itself was healthy throughout — `xdpyinfo` against `:1` with the GDM
Xauthority connected cleanly. Only x11vnc's internal handle was dead.

## Fix

`scripts/operations/connection/vnc-ace-linux-2.sh` — replaced the
"start only if port not bound" block with an **ensure-fresh** block that:

- detects the display from the live X socket (`/tmp/.X11-unix/`) — works for
  both Xorg and Xwayland;
- detects auth via Xorg/Xwayland `-auth` → GDM Xauthority → mutter Xwayland auth
  → `guess` (Wayland-aware fallback chain);
- **verifies the display is reachable** (`xdpyinfo`) before launching, reporting
  `UNREACHABLE` (instead of a silently-broken server) when no one is logged in;
- **always kills and relaunches** x11vnc rather than trusting a bound port;
- logs to `/tmp/x11vnc.log` (not `/dev/null`) for debuggability.

Dropped the `-noshm -noxdamage -noscr` flags and the sudo branch (on this box
x11vnc runs as `vamsee` with a user-readable GDM auth; a root-owned display now
surfaces as `UNREACHABLE`).

## Verification (evidence)

- New remote ensure-block run end-to-end against `ace-linux-2` →
  `OK display=:1 auth=/run/user/1000/gdm/Xauthority`; killed the prior instance,
  relaunched fresh, 0.0% CPU at launch.
- `bash -n` syntax check passed.
- Live confirmation: after re-running the helper, x11vnc (pid 999781) is serving
  a real interactive session (log shows keyboard/autorepeat events).

## Repo state

- **Commit:** `c1a27d2c8` `fix(vnc): ensure-fresh x11vnc on ace-linux-2; Wayland-aware auth detection` on `main`.
- A **3-hour-stale `.git/index.lock`** (14:32) was removed to commit — no owning
  process; reflog confirms clean sequential history afterward.
- `main` is `ahead 11, behind 6` of `origin/main` amid heavy parallel automation
  (solver dashboard, provider-kanban, autosync). **Not pushed by this session** —
  the autosync hook / a later reconcile handles push safely; pushing now would
  require merging the 6 behind-commits and risk racing concurrent sessions.

## External actions

- **None outward-facing.** No GitHub issue, no email, no published artifact.
- Side effect on `ace-linux-2`: killed the stale x11vnc and started a fresh one
  (the fix's purpose); runtime log at `/tmp/x11vnc.log`.

## Next steps / open items

- None required. The helper now self-heals on each run.
- Optional follow-on: record the "port-bound ≠ healthy / Wayland auth path"
  lesson in `.claude/memory/KNOWLEDGE.md` (held off — the fix is self-documenting
  in the script comments).
- If desired, promote x11vnc to a systemd unit on `ace-linux-2` so it restarts
  with the graphical session (eliminates the stale-handle window entirely).
