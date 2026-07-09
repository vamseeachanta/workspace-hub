---
name: reference-ace-linux-2-headless-vnc
description: "How to reach ace-linux-2's desktop — it is headless (no physical :0); remote desktop = TigerVNC :1 / port 5901"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 453b4af3-a85c-49c8-8032-967d1442cf23
---

`ace-linux-2` is **headless** — no monitor, nobody logs in physically. Its physical `:0` is only ever the GDM greeter (`WaylandEnable=false` + `AutomaticLogin=vamsee` in `/etc/gdm3/custom.conf`, but the greeter sits idle). So `x11vnc`-attach-to-`:0` fundamentally cannot work there — that was the old bug in `vnc-ace-linux-2.sh`.

**The desktop is a TigerVNC virtual server on display `:1` / port `5901`**, owning its own framebuffer:
- Config: `~/.vnc/config` on the box — `geometry=1920x1080`, `depth=24`, `localhost`, `SecurityTypes=None`. SSH is the auth boundary (localhost-only bind + your SSH key); no VNC password by design.
- `~/.vnc/xstartup` launches full GNOME via `dbus-run-session -- gnome-session --disable-acceleration-check` (the flag is required — headless = no GPU).
- Boot-persistent via `tigervncserver@:1.service` (enabled 2026-07-02). Mapping is `:1=vamsee` in `/etc/tigervnc/vncserver.users`.

**To connect** (from ace-linux-1): `bash workspace-hub/scripts/operations/connection/vnc-ace-linux-2.sh` — rewritten 2026-07-02 to ensure `:1` is healthy (port listening AND `xdpyinfo` answers, else kill+relaunch), tunnel `5901`, launch `xtigervncviewer`. Manual equivalent: `ssh -L 5901:localhost:5901 vamsee@ace-linux-2 -N &` then `xtigervncviewer localhost:5901`.

Change resolution/security by editing `~/.vnc/config` on ace-linux-2 (single source of truth — the launcher passes no geometry/security flags). Relates to [[project_voice_dictation_ecosystem]] (parked VNC voice track).
