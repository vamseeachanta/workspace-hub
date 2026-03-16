---
name: workspace-cli-keyboard-navigation
description: 'Sub-skill of workspace-cli: Keyboard Navigation (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Keyboard Navigation (+2)

## Keyboard Navigation


- **Number keys**: Select menu options
- **0**: Go back / Exit
- **Ctrl+C**: Force exit


## Direct Access


Skip menus with direct commands:

```bash
# Instead of navigating menus
./scripts/workspace

# Use direct script path
./scripts/repository_sync sync all -m "Quick update"
```


## Command Aliases


Add to `.bashrc` or `.zshrc`:

```bash
# Workspace CLI aliases
alias ws='./scripts/workspace'
alias rs='./scripts/repository_sync'
alias rsync='./scripts/repository_sync sync all'
alias rstatus='./scripts/repository_sync status all'
alias rpull='./scripts/repository_sync pull all'
```
