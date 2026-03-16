---
name: workspace-cli-menu-display-issues
description: 'Sub-skill of workspace-cli: Menu Display Issues (+3).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Menu Display Issues (+3)

## Menu Display Issues


```bash
# Check terminal supports ANSI
echo $TERM

# Run with basic terminal
TERM=xterm ./scripts/workspace
```


## Script Not Found


```bash
# Verify workspace root
pwd
# Should be: /mnt/github/workspace-hub

# Make scripts executable
chmod +x ./scripts/workspace
chmod +x ./scripts/*/*.sh
```


## Permission Denied


```bash
# Fix permissions
chmod +x ./scripts/workspace
chmod +x ./scripts/*/*.sh
chmod +x ./scripts/*/*.py
```


## Configuration Missing


```bash
# Run configuration helper
./scripts/repository/configure_repos.sh

# Or edit directly
nano config/repos.conf
```
