---
name: workspace-cli-1-repository-management
description: 'Sub-skill of workspace-cli: 1. Repository Management (+4).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Repository Management (+4)

## 1. Repository Management


Access multi-repository git operations:

```
Repository Management:

  1) Repository Sync Manager       # Full git operations menu
  2) Configure Repository URLs     # Setup GitHub URLs
  3) Check All Repository Status   # Quick status overview

  0) Back to main menu
```

**Common Operations:**

```bash
# List all repositories
./scripts/repository_sync list all

# Sync all work repositories
./scripts/repository_sync sync work -m "Update"

# Pull latest from all repos
./scripts/repository_sync pull all

# Check status
./scripts/repository_sync status all
```


## 2. Compliance & Standards


Enforce coding standards and guidelines:

```
Compliance & Standards:

  1) Propagation Tools            # Spread standards
  2) Compliance Enforcement       # Setup and hooks
  3) Verification Tools           # Check status

  0) Back to main menu
```

**Propagation Tools:**
```bash
# Sync CLAUDE.md to all repos
./scripts/compliance/propagate_claude_config.py

# Sync AI guidelines
./scripts/compliance/propagate_guidelines.sh

# Enable interactive mode
./scripts/compliance/propagate_interactive_mode.sh
```

**Enforcement:**
```bash
# Initial setup
./scripts/compliance/setup_compliance.sh

# Install git hooks
./scripts/compliance/install_compliance_hooks.sh

# Verify compliance
./scripts/compliance/verify_compliance.sh
```


## 3. Remote Connection Tools


Manage remote workspace connections:

```
Remote Connection Tools:

  1) Linux Connection Tools
  2) Windows Connection Tools
  3) Tailscale Connection Tools

  0) Back to main menu
```

**Linux:**
```bash
./scripts/connection/connect-workspace-linux.sh
./scripts/connection/sync-tabby-linux.sh
```

**Windows:**
```powershell
./scripts/connection/connect-workspace-windows.ps1
./scripts/connection/sync-tabby-windows.ps1
```

**Tailscale:**
```bash
./scripts/connection/connect-workspace-tailscale.sh    # Bash
./scripts/connection/connect-workspace-tailscale.ps1   # PowerShell
```


## 4. Development Tools


AI-powered development and code quality:

```
Development Tools:

  1) Factory.ai Tools             # Install Factory.ai
  2) Refactor Analysis            # Code quality analysis
  3) Droid CLI                    # Factory.ai droid wrapper

  0) Back to main menu
```

**Refactor Analysis:**
```bash
# Run full analysis
./scripts/development/refactor-analysis.sh

# Output in .refactor-reports/
```

Analysis includes:
- Code duplication (jscpd)
- Dead code detection (knip)
- Slow test identification
- Large file detection
- Outdated dependencies

**Factory.ai:**
```bash
# Install Factory.ai
./scripts/development/install_factory_ai.sh

# Use droid CLI
./scripts/development/droid --help
```


## 5. System Setup & Configuration


System-level configuration:

```
System Setup & Configuration:

  1) Workspace Sync               # Full workspace sync
  2) Setup XRDP                   # Remote desktop
  3) View System Information      # Workspace stats

  0) Back to main menu
```

**Workspace Sync:**
```bash
./scripts/system/sync
```

Performs:
- Git repository synchronization
- MCP server installation
- UV environment setup
- NPM package management
- Agent configuration
