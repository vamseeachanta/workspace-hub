---
name: ace-linux-2-desktop-crash-recovery
description: "a2 \"only logout screen\" = gnome-shell segfault fail-whale, NOT always nvidia; recovery runbook + x11vnc display gotcha"
metadata: 
  node_type: memory
  type: project
  originSessionId: 832b1e39-7150-4d86-9bdc-116a7baed592
---

2026-06-10: ace-linux-2 showed only a "logout screen" — this time NOT the [[ace-linux-2-nvidia-hold-drift]] driver/kernel mismatch (driver 580.159.03 matched kernel 6.17.0-35, nvidia-smi clean). Cause: gnome-shell SEGV (signal 11) → `gnome-session-failed --allow-logout` fullscreen fail-whale on :0; systemd had already respawned a healthy shell underneath. Crash dump: /var/crash/_usr_bin_gnome-shell.1000.crash.

**Recovery runbook (remote, from a1):**
1. Diagnose: `ps aux | grep gnome-session-failed`; crash files in /var/crash; journal `--user -u org.gnome.Shell@x11.service`.
2. Killing gnome-session-failed tears down the whole session → gdm greeter (apps lost). Acceptable; gdm has `AutomaticLogin=vamsee` in /etc/gdm3/custom.conf but autologin only fires on gdm START, so user must run `ssh -t ace-linux-2 'sudo systemctl restart gdm3'` (sudo NEEDS password on a2; classifier blocks agent-side remote kills/restarts — route via `!` prefix).
3. x11vnc does NOT come back by itself: `~/.config/autostart/x11vnc.desktop` had stale `-display :1` (desktop is :0; :1 = old headless dbus-run-session secondary). Fixed to :0 on 2026-06-10. If dead again: `x11vnc -display :0 -auth /run/user/1000/gdm/Xauthority -forever -nopw -listen localhost -rfbport 5900 -bg -o /tmp/x11vnc.log`.

Open hardware flag: a2 /dev/sda = WD Blue 1TB (WD10EZEX, serial WCC3F6EFP0TX) holding **/mnt/local-analysis** (data disk; OS is on Samsung SSD sdb). 2026-06-10 SMART: **68,583 power-on hours (~7.8 yr)**, 1 Current_Pending_Sector, 0 reallocated, Multi_Zone_Error_Rate raw=1, no CRC/log errors, overall PASSED. Extended self-test 2026-06-10: **completed without error** (smartd 07:15 poll) but pending count stayed 1 → marginal/stale sector, readable on this pass, will clear/remap on next write to that LBA; no spreading defect. Risk driver = AGE not the sector. Plan: replace drive (1TB SATA SSD), verify what on /mnt/local-analysis isn't git-pushed; smartd already alerts if pending grows or reallocations start. sudo needs password on a2 → any smartctl read goes through the user. **Durable tracker = wshub #3026** (incident writeup + replacement/backup-inventory checklist; also carries the #1581 nvidia-blacklist-removal leftover).
