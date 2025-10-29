# Tabby Terminal Configuration

Centralized Tabby terminal configuration for syncing across Linux and Windows machines.

## Installation

### Linux

```bash
# Download and install Tabby
wget https://github.com/Eugeny/tabby/releases/latest/download/tabby-1.0.228-linux-x64.deb
sudo dpkg -i tabby-1.0.228-linux-x64.deb

# Sync config from workspace-hub
./scripts/sync-tabby-linux.sh
```

### Windows

1. **Download Tabby installer:**
   - Visit: https://github.com/Eugeny/tabby/releases/latest
   - Download: `tabby-1.0.228-setup-x64.exe`
   - Run installer

2. **Clone workspace-hub (if not already):**
   ```powershell
   cd C:\
   git clone https://github.com/yourusername/workspace-hub.git
   ```

3. **Sync config:**
   ```powershell
   cd C:\workspace-hub
   .\scripts\sync-tabby-windows.ps1
   ```

## Configuration

### Config Location

- **Linux:** `~/.config/tabby/config.yaml`
- **Windows:** `%APPDATA%\tabby\config.yaml`
- **Workspace Hub:** `config/tabby/config.yaml`

### Default Settings

- **Theme:** Dark (Tabby Default)
- **Hotkeys:**
  - `Ctrl+Space` - Toggle window
  - `Ctrl+Shift+T` - New tab
  - `Ctrl+Shift+W` - Close tab
  - `Alt+1-5` - Switch to tab 1-5
- **Terminal:**
  - Font: monospace, 12pt
  - Copy on select: enabled
  - Right-click: paste

### Customization

Edit `config/tabby/config.yaml` in workspace-hub, then run sync script on each machine.

## Syncing Workflow

### After Making Changes

**On Linux:**
```bash
# Copy local config to workspace-hub
cp ~/.config/tabby/config.yaml /mnt/github/workspace-hub/config/tabby/

# Commit and push
cd /mnt/github/workspace-hub
git add config/tabby/
git commit -m "Update Tabby config"
git push
```

**On Windows:**
```powershell
# Copy local config to workspace-hub
Copy-Item "$env:APPDATA\tabby\config.yaml" "C:\workspace-hub\config\tabby\"

# Commit and push
cd C:\workspace-hub
git add config\tabby\
git commit -m "Update Tabby config"
git push
```

### After Pulling Changes

**On Linux:**
```bash
cd /mnt/github/workspace-hub
git pull
./scripts/sync-tabby-linux.sh
```

**On Windows:**
```powershell
cd C:\workspace-hub
git pull
.\scripts\sync-tabby-windows.ps1
```

## Advanced Setup

### Adding Plugins

1. Install plugin in Tabby UI (Settings > Plugins)
2. Copy plugin files:
   - **Linux:** `~/.config/tabby/plugins/` → `config/tabby/plugins/`
   - **Windows:** `%APPDATA%\tabby\plugins\` → `config\tabby\plugins\`
3. Commit to workspace-hub
4. Run sync script on other machines

### Custom Themes

Edit `terminal.colorScheme` in `config.yaml`:

```yaml
terminal:
  colorScheme:
    name: Custom Dark
    foreground: '#e0e0e0'
    background: '#1a1a1a'
    cursor: '#00ff00'
    colors:
      - '#000000'
      - '#ff0000'
      # ... 14 more colors
```

### SSH Profiles

Add SSH profiles to `profiles` section:

```yaml
profiles:
  - name: My Server
    type: ssh
    options:
      host: example.com
      user: username
      port: 22
```

## Troubleshooting

**Config not applying:**
- Ensure Tabby is completely closed (check system tray)
- Delete `~/.config/tabby/Preferences` (Linux) or `%APPDATA%\tabby\Preferences` (Windows)
- Restart Tabby

**Sync script fails:**
- Verify workspace-hub path is correct
- Check file permissions
- Ensure Tabby is installed and in PATH

**Colors wrong:**
- Check terminal color scheme settings
- Verify config.yaml syntax (YAML is indent-sensitive)

## Resources

- **Tabby Documentation:** https://tabby.sh/
- **GitHub Repository:** https://github.com/Eugeny/tabby
- **Plugin Directory:** https://github.com/Eugeny/tabby/wiki/Plugins
