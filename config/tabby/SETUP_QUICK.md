# Tabby Terminal - Quick Setup Guide

## Linux Setup (Current Machine)

✓ Already installed and configured!

To sync config after pulling updates:
```bash
cd /mnt/github/workspace-hub
git pull
./scripts/sync-tabby-linux.sh
```

## Windows Setup (New Machine)

### Step 1: Install Tabby

1. Download installer from: https://github.com/Eugeny/tabby/releases/latest
2. Get file: `tabby-1.0.228-setup-x64.exe`
3. Run installer (standard installation)

### Step 2: Clone Workspace Hub

```powershell
# Open PowerShell as Administrator (optional, but recommended)
cd C:\
git clone https://github.com/yourusername/workspace-hub.git
```

### Step 3: Sync Config

```powershell
cd C:\workspace-hub
.\scripts\sync-tabby-windows.ps1
```

### Step 4: Restart Tabby

Close Tabby completely and reopen to apply settings.

## Making Changes

### On Any Machine

1. Edit settings in Tabby UI
2. Copy config back to workspace-hub:

**Linux:**
```bash
cp ~/.config/tabby/config.yaml /mnt/github/workspace-hub/config/tabby/
```

**Windows:**
```powershell
Copy-Item "$env:APPDATA\tabby\config.yaml" "C:\workspace-hub\config\tabby\"
```

3. Commit and push:
```bash
git add config/tabby/
git commit -m "Update Tabby config"
git push
```

4. Pull on other machines and run sync script

## Features Included

- Dark theme optimized for coding
- Keyboard shortcuts (Alt+1-5 for tab switching)
- Copy on select enabled
- Right-click to paste
- Custom hotkeys for productivity

## Troubleshooting

**Config not applying?**
- Completely close Tabby (check system tray)
- Run sync script again
- Restart Tabby

**Script fails on Windows?**
- Run PowerShell as Administrator
- Check workspace path in script
- Verify Tabby is installed

**Need help?**
See full documentation in `config/tabby/README.md`
