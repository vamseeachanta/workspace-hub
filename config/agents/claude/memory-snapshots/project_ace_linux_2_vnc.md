---
name: ace-linux-2-vnc-setup
description: Configured VNC state on ace-linux-2 — TigerVNC vncserver@:1 user-systemd, localhost-only on port 5901, SecurityTypes=None gated by SSH; replaces broken x11vnc.service
type: project
originSessionId: 31e065de-df6a-44e0-9c18-5025ace15758
---
ace-linux-2 VNC was rebuilt 2026-04-27. The old `x11vnc.service` user-unit had crashlooped 67,189 times since boot because the host has no graphical login (SSH/Tailscale only). Now serves desktop via TigerVNC `vncserver@:1.service` (user-level, lingering): `Xtigervnc` on `127.0.0.1:5901` only, `SecurityTypes=None`, GNOME via Xorg, geometry 1920x1080.

**Why:** ace-linux-2 is the dev-secondary on Tailscale 10.1.0.2 — operated headlessly. x11vnc is a screen-mirror, fundamentally wrong for headless; TigerVNC `vncserver` creates its own X display, doesn't depend on a logged-in user.

**How to apply:**
- Connect: `scripts/operations/connection/vnc-ace-linux-2.sh` (auto-tunnels 5901, launches xtigervncviewer with `-SecurityTypes None`)
- Manual ops: `ssh ace-linux-2 'systemctl --user {status,restart,stop} vncserver@:1.service'`
- Config files: `~/.vnc/config`, `~/.vnc/xstartup`, `~/.config/systemd/user/vncserver@.service`
- Old `x11vnc.service` is stopped + disabled (unit file still present but harmless)
- Linger is enabled for `vamsee` so service survives logout
- Bind is **localhost-only** (127.0.0.1 + [::1]); no auth on the VNC layer because access requires SSH (which provides auth + transport encryption). If exposing to LAN/Tailscale, switch to `SecurityTypes=VncAuth` and `vncpasswd`.
- Companion runbook: `.claude/skills/operations/devops/remote-desktop-headless-ubuntu/SKILL.md`
- Rollback: `systemctl --user disable --now vncserver@:1.service && rm -rf ~/.vnc ~/.config/systemd/user/vncserver@.service`
