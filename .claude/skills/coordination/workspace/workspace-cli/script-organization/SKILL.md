---
name: workspace-cli-script-organization
description: 'Sub-skill of workspace-cli: Script Organization.'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Script Organization

## Script Organization


```
scripts/
+-- workspace                    # Main CLI entry point
|
+-- repository/                  # Repository management
|   +-- configure_repos.sh
|   +-- check_all_status.sh
|
+-- compliance/                  # Compliance tools
|   +-- propagate_claude_config.py
|   +-- propagate_guidelines.sh
|   +-- propagate_interactive_mode.sh
|   +-- setup_compliance.sh
|   +-- install_compliance_hooks.sh
|   +-- verify_compliance.sh
|
+-- connection/                  # Remote connections
|   +-- connect-workspace-linux.sh
|   +-- connect-workspace-windows.ps1
|   +-- connect-workspace-tailscale.sh
|   +-- connect-workspace-tailscale.ps1
|   +-- sync-tabby-linux.sh
|   +-- sync-tabby-windows.ps1
|
+-- development/                 # Development tools
|   +-- install_factory_ai.sh
|   +-- refactor-analysis.sh
|   +-- droid
|
+-- system/                      # System configuration
    +-- sync
    +-- setup_xrdp.sh
```
