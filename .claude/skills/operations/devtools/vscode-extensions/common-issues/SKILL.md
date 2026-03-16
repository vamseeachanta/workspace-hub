---
name: vscode-extensions-common-issues
description: 'Sub-skill of vscode-extensions: Common Issues.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Extensions not loading**
```bash
# Check extension host logs
# Help -> Toggle Developer Tools -> Console

# Reinstall extension
code --uninstall-extension extension-id
code --install-extension extension-id

# Reset VS Code
rm -rf ~/.config/Code/CachedData
```

**Issue: Slow startup**
```bash
# Profile startup
code --prof-startup

# Disable extensions
code --disable-extensions

# Check extension impact
# Help -> Startup Performance
```

**Issue: IntelliSense not working**
```bash
# Restart language server
# Cmd/Ctrl+Shift+P -> "Restart Extension Host"

# Clear workspace cache
rm -rf .vscode/.ropeproject
rm -rf __pycache__
```

**Issue: Settings not applying**
```bash
# Check settings precedence:
# 1. Workspace settings (.vscode/settings.json)
# 2. User settings (settings.json)
# 3. Default settings

# View effective settings
# Cmd/Ctrl+Shift+P -> "Preferences: Open Settings (JSON)"
```
