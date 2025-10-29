# Tabby Remote Access - Quick Reference

## Connection Info

### Local Network (Same WiFi)
```
Host:     192.168.1.100
User:     vamsee
Hostname: vamsee-linux1
Port:     22
```

### Tailscale VPN (Anywhere on Internet)
```
Host:     100.107.64.76
User:     vamsee
Hostname: vamsee-linux1
Port:     22
Network:  Tailscale VPN
```

## From Windows Machine

### Method 1: Tabby (Recommended)
```powershell
# One-time setup
cd C:\workspace-hub
.\scripts\sync-tabby-windows.ps1

# Connect (choose based on location)
# Local: Open Tabby → "Linux Workspace (Local Network)"
# Internet: Open Tabby → "Linux Workspace (Tailscale - Internet)"
```

### Method 2: Quick Scripts
```powershell
# Local network
cd C:\workspace-hub
.\scripts\connect-workspace-windows.ps1

# Tailscale (internet)
.\scripts\connect-workspace-tailscale.ps1
```

### Method 3: Direct SSH
```powershell
# Local network
ssh vamsee@192.168.1.100

# Tailscale (internet)
ssh vamsee@100.107.64.76
```

## From Linux/Mac Machine

### Method 1: Tabby (Recommended)
```bash
# One-time setup
./scripts/sync-tabby-linux.sh

# Connect (choose based on location)
# Local: Open Tabby → "Linux Workspace (Local Network)"
# Internet: Open Tabby → "Linux Workspace (Tailscale - Internet)"
```

### Method 2: Quick Scripts
```bash
# Local network
./scripts/connect-workspace-linux.sh

# Tailscale (internet)
./scripts/connect-workspace-tailscale.sh
```

### Method 3: Direct SSH
```bash
# Local network
ssh vamsee@192.168.1.100

# Tailscale (internet)
ssh vamsee@100.107.64.76
```

## Setup SSH Keys (Passwordless)

**On remote machine:**
```bash
# Generate key (if needed)
ssh-keygen -t ed25519

# Copy to workspace
ssh-copy-id vamsee@192.168.1.100

# Test
ssh vamsee@192.168.1.100
```

## Tabby Shortcuts

| Action | Shortcut |
|--------|----------|
| Toggle window | `Ctrl+Space` |
| New tab | `Ctrl+Shift+T` |
| Close tab | `Ctrl+Shift+W` |
| Switch tab 1-5 | `Alt+1` to `Alt+5` |
| Split vertical | `Ctrl+Shift+E` |
| Split horizontal | `Ctrl+Shift+D` |

## File Transfer

**Upload to workspace:**
```bash
scp file.txt vamsee@192.168.1.100:~/
```

**Download from workspace:**
```bash
scp vamsee@192.168.1.100:~/file.txt ./
```

**Using Tabby:**
1. Connect via SSH
2. Right-click → "Open SFTP panel"
3. Drag and drop files

## Persistent Sessions (tmux)

**On workspace machine:**
```bash
# Start tmux
tmux new -s work

# Detach: Ctrl+B then D

# Later, reattach
tmux attach -t work
```

## Troubleshooting

**Cannot connect:**
```bash
# Check SSH on workspace
sudo systemctl status ssh

# Check firewall
sudo ufw status
sudo ufw allow 22
```

**Connection drops:**
Add to `~/.ssh/config` on remote machine:
```
Host workspace
    HostName 192.168.1.100
    User vamsee
    ServerAliveInterval 60
```

## Files Location

| Item | Location |
|------|----------|
| Config | `config/tabby/config.yaml` |
| Sync script (Linux) | `scripts/sync-tabby-linux.sh` |
| Sync script (Windows) | `scripts\sync-tabby-windows.ps1` |
| Connect script (Linux) | `scripts/connect-workspace-linux.sh` |
| Connect script (Windows) | `scripts\connect-workspace-windows.ps1` |
| Full docs | `config/tabby/REMOTE_ACCESS.md` |

## After Config Changes

```bash
# Pull updates
cd /path/to/workspace-hub
git pull

# Sync config
./scripts/sync-tabby-linux.sh        # Linux
.\scripts\sync-tabby-windows.ps1    # Windows

# Restart Tabby
```
