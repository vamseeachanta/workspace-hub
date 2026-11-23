# Session Handoff — ace-linux-2 NVIDIA hold-drift fix (VNC/desktop restored)

**Date:** 2026-06-04 | **Machine:** ace-linux-1 (Claude session) acting on ace-linux-2 | **Issue:** [#1581](https://github.com/vamseeachanta/workspace-hub/issues/1581)

## Outcome

ace-linux-2 desktop, GPU, and VNC are **fully restored and user-verified**:

| Check | Result |
|---|---|
| Kernel | 6.17.0-35-generic (rebooted 2026-06-04 ~14:50 CT after 42 days uptime) |
| NVIDIA | T400 4GB, driver 580.159.03, `nvidia-smi` healthy (dead since ≥ Apr 27) |
| Display | Xorg vt2, GDM auto-login, 1920x1080@60 on DP-0 via CustomEDID |
| VNC | `scripts/operations/connection/vnc-ace-linux-2.sh` connects; user confirmed improved view |

## Root cause (structural — explains every #1581 recurrence)

1. **2026-02-22:** NVIDIA stack apt-held (17 pkgs) + `nvidia`/`libnvidia` blacklisted in `/etc/apt/apt.conf.d/50unattended-upgrades` → driver frozen at 580.126.09.
2. Kernels kept auto-upgrading (-14 → -19 → -20 → -22 → -35 on disk); machine ran -22 since Apr 22, no reboots.
3. Ubuntu per-kernel NVIDIA module packages **hard-pin the driver point release** (e.g. `linux-modules-nvidia-580-open-6.17.0-22-generic` Depends `nvidia-kernel-common-580 (>= 580.142, <= 580.142-1)`), and superseded point releases are **deleted from the archive** → a held NVIDIA stack has a built-in expiry date; modules for new kernels become permanently uninstallable.
4. Missing `nvidia.ko` → `nvidia-drm` absent → Xorg's OutputClass ModulePath for the nvidia X driver never activates → `(EE) Failed to load module "nvidia"` despite `xserver-xorg-video-nvidia-580` installed.
5. WRK-307 KVM/EDID configs (`/etc/X11/xorg.conf.d/10-force-display.conf`, `10-virtual-display.conf`) hard-require `Driver "nvidia"` → no modesetting fallback → gnome session crash-loop → no `:0` → x11vnc has nothing to mirror.

## Fix applied (by VA with sudo, guided by session)

```
sudo apt-mark unhold <all 17 nvidia pkgs>
sudo apt-get full-upgrade   # 44 pkgs: stack → 580.159.03, -35 modules in, stale -19/-20 module pkgs out
sudo reboot                 # lands on already-installed 6.17.0-35
```

## Open items (next session / VA)

1. **Recurrence killer (NOT yet done):** comment out `"nvidia"`/`"libnvidia"` in `Unattended-Upgrade::Package-Blacklist` on ace-linux-2, or drift restarts at the next driver point release. Ready-to-run command is in the #1581 thread context (sed with `.bak-20260604` backup).
2. Optional hardening from machine notes: DP EDID emulator dongle (~$10) permanently fixes the WRK-307 KVM issue and would let the force-nvidia Xorg confs be deleted, restoring modesetting fallback.
3. Watch on next kernel bump: DRM card renumbering can stale the captured EDID path (per machine notes) — first suspect if display degrades again.

## Diagnostic shortcuts learned (also in Claude auto-memory `project_ace_linux_2_nvidia_hold_drift`)

- GDM auto-login fires **once per gdm start** — after logout/session-crash the machine sits at the greeter forever; `systemctl restart gdm3` re-triggers it.
- `systemctl status gdm` ActiveSince timestamp = ground truth for whether a remote restart actually executed.
- Claude Code's `!` prefix cannot allocate a TTY → `ssh -t … sudo` fails with "a terminal is required"; sudo commands must run in a real terminal.
- `pkill -f <pattern>` over SSH self-kills when the pattern matches the wrapping `bash -c` — kill by PID.

## Repo / external state at exit

- **workspace-hub (ace-linux-1):** on branch `fix/track-fleet-skills-2925-portable` (93 behind origin/main, pre-existing), dirty runtime files (`statusline-command.sh`, quota JSONs) — pre-existing, untouched by this session.
- **External actions taken:** [#1581 root-cause comment](https://github.com/vamseeachanta/workspace-hub/issues/1581#issuecomment-4625594184); this handoff PR. Nothing else posted/sent.
- **ace-linux-2:** healthy; x11vnc serving localhost:5900 (by design); no stale session probes (cleaned during diagnosis).
