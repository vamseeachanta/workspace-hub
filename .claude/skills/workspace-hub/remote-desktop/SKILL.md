---

name: remote-desktop
description: Connect to dev-secondary graphical desktop from dev-primary via VNC over SSH tunnel
version: "1.0.0"
category: workspace-hub
---

# Remote Desktop — dev-secondary

Connect to dev-secondary graphical desktop from dev-primary via VNC over SSH tunnel.

## Quick Start

```bash
bash scripts/operations/connection/vnc-dev-secondary.sh
```

Script is fully self-contained: detects display+auth, auto-starts x11vnc if needed, opens tunnel, launches viewer.

## How It Works

1. Checks if x11vnc is listening on port 5900
2. If not: parses live Xorg `ps` entry to find display + auth file dynamically
3. Starts x11vnc (no sudo if vamsee owns display; sudo prompt if GDM/root owns it)
4. Opens SSH tunnel `localhost:5900 → dev-secondary:5900`
5. Launches `xtigervncviewer localhost:5900`

## Required Flags (Hard-Won)

| Flag | Why Required |
|---|---|
| `-noshm` | MIT-SHM denied when x11vnc user ≠ X server owner |
| `-noxdamage` | GNOME/Mutter compositor causes XIO crash via XDAMAGE |
| `-noscr` | GNOME conflicts with RECORD extension scroll detection |
| `-auth <explicit-path>` | `-auth guess` fails when running as root on GDM display |
| `-o /dev/null` | Avoids stale root-owned log file permission errors |

## Auth File Location

Resolved dynamically from `ps wwwaux | grep Xorg`:
- **GDM only (no user login)**: `/run/user/120/gdm/Xauthority` — requires sudo
- **User session active**: `/run/user/1000/gdm/Xauthority` — no sudo needed

## Persistent Setup (Optional)

To avoid needing to start x11vnc each time, create a systemd service on dev-secondary:

```bash
sudo tee /etc/systemd/system/x11vnc.service <<'EOF'
[Unit]
Description=x11vnc VNC server for display :0
After=display-manager.service
Requires=display-manager.service

[Service]
ExecStart=/usr/bin/x11vnc -display :0 -auth /run/user/120/gdm/Xauthority -noshm -noxdamage -noscr -forever -nopw -listen localhost -rfbport 5900
Restart=on-failure
RestartSec=3

[Install]
WantedBy=graphical.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now x11vnc
```

Note: systemd service uses GDM auth path — update if user session display changes.

## Viewer Notes

- `SetDesktopSize failed: 1` — harmless; physical display ignores client resize requests
- `End of stream` immediately — x11vnc not running; rerun the script
- `Connection refused` — SSH tunnel failed or nothing on port 5900
