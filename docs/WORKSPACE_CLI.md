# Workspace CLI - Unified Management Console

> Unified multi-level menu system for workspace-hub management
>
> Version: 1.0.0
> Last Updated: 2025-10-26

## Overview

The Workspace CLI provides a unified, organized interface to all workspace management tools through an intuitive 3-level menu system. All scripts have been reorganized into logical categories for better maintainability and discoverability.

## Quick Start

### Launch Interactive Menu
```bash
./scripts/workspace
```

### Direct Script Access
```bash
# Repository management
./scripts/repository/configure_repos.sh

# Compliance tools
./scripts/compliance/verify_compliance.sh

# Development tools
./scripts/development/refactor-analysis.sh

# System tools
./scripts/system/sync
```

---

## Menu Structure

### Level 1: Main Categories

```
╔════════════════════════════════════════════════════════════════╗
║              Workspace Hub - Management Console               ║
╚════════════════════════════════════════════════════════════════╝

Workspace Management:

  1) Repository Management
  2) Compliance & Standards
  3) Remote Connection Tools
  4) Development Tools
  5) System Setup & Configuration
  6) Help & Documentation

  0) Exit
```

---

## Category Details

### 1. Repository Management

**Purpose:** Manage multiple Git repositories with unified operations

**Level 2 Options:**
1. **Repository Sync Manager** → Full multi-repo git operations (interactive menu)
2. **Configure Repository URLs** → Setup GitHub URLs for all repositories
3. **Check All Repository Status** → Quick status overview of all repos

**Key Features:**
- Multi-repository git operations (commit, push, pull, sync)
- Branch management (list, fetch, sync-main, switch)
- Work/Personal repository categorization
- URL configuration helper
- Status monitoring

**Related Scripts:**
- `repository_sync` (main CLI in workspace root)
- `scripts/repository/configure_repos.sh`
- `scripts/repository/check_all_status.sh`

---

### 2. Compliance & Standards

**Purpose:** Enforce coding standards and AI usage guidelines across repositories

**Level 2 Options:**
1. **Propagation Tools** → Submenu for spreading standards
2. **Compliance Enforcement** → Submenu for setup and hooks
3. **Verification Tools** → Check compliance status

**Level 3: Propagation Tools**
1. **Propagate Claude Configuration** → Sync CLAUDE.md to all repos
2. **Propagate Guidelines** → Sync AI usage guidelines
3. **Propagate Interactive Mode** → Enable question-asking mode

**Level 3: Compliance Enforcement**
1. **Setup Compliance** → Initial compliance configuration
2. **Install Compliance Hooks** → Git hooks for validation
3. **Verify Compliance** → Check current status

**Related Scripts:**
- `scripts/compliance/propagate_claude_config.py`
- `scripts/compliance/propagate_guidelines.sh`
- `scripts/compliance/propagate_interactive_mode.sh`
- `scripts/compliance/setup_compliance.sh`
- `scripts/compliance/install_compliance_hooks.sh`
- `scripts/compliance/verify_compliance.sh`

---

### 3. Remote Connection Tools

**Purpose:** Manage remote workspace connections and terminal configurations

**Level 2 Options:**
1. **Linux Connection Tools** → Submenu
2. **Windows Connection Tools** → Submenu
3. **Tailscale Connection Tools** → Submenu

**Level 3: Linux Connection Tools**
1. **Connect to Workspace (Linux)** → Standard SSH connection
2. **Sync Tabby Configuration (Linux)** → Terminal config sync

**Level 3: Windows Connection Tools**
1. **Connect to Workspace (Windows)** → PowerShell connection script
2. **Sync Tabby Configuration (Windows)** → Terminal config sync

**Level 3: Tailscale Connection Tools**
1. **Connect via Tailscale (Bash)** → Linux/Mac Tailscale connection
2. **Connect via Tailscale (PowerShell)** → Windows Tailscale connection

**Related Scripts:**
- `scripts/connection/connect-workspace-linux.sh`
- `scripts/connection/connect-workspace-windows.ps1`
- `scripts/connection/connect-workspace-tailscale.sh`
- `scripts/connection/connect-workspace-tailscale.ps1`
- `scripts/connection/sync-tabby-linux.sh`
- `scripts/connection/sync-tabby-windows.ps1`

---

### 4. Development Tools

**Purpose:** AI-powered development and code quality tools

**Level 2 Options:**
1. **Factory.ai Tools** → Install and configure Factory.ai integration
2. **Refactor Analysis** → Code quality and refactoring analysis
3. **Droid CLI** → Factory.ai droid command wrapper

**Key Features:**
- Code duplication detection (jscpd)
- Dead code detection (knip)
- Slow test identification
- Large file detection
- Outdated dependency scanning
- AI-assisted development with Factory.ai droids

**Related Scripts:**
- `scripts/development/install_factory_ai.sh`
- `scripts/development/refactor-analysis.sh`
- `scripts/development/droid`

---

### 5. System Setup & Configuration

**Purpose:** System-level configuration and workspace synchronization

**Level 2 Options:**
1. **Workspace Sync** → Full workspace synchronization (repos, MCP, npm, etc.)
2. **Setup XRDP (Remote Desktop)** → Configure remote desktop access
3. **View System Information** → Display workspace details and statistics

**Key Features:**
- Git repository synchronization
- MCP server installation
- UV environment setup
- NPM package management
- Agent configuration management
- System information display

**Related Scripts:**
- `scripts/system/sync`
- `scripts/system/setup_xrdp.sh`

---

### 6. Help & Documentation

**Purpose:** Access documentation and help resources

**Level 2 Options:**
1. **Repository Sync Documentation** → View repository_sync help
2. **View README** → Main workspace documentation
3. **Available Commands** → List all CLI commands
4. **Quick Start Guide** → Getting started tutorial

---

## Script Organization

### Directory Structure

```
scripts/
├── repository/              # Repository management tools
│   ├── configure_repos.sh   # URL configuration helper
│   └── check_all_status.sh  # Quick status check
│
├── compliance/              # Compliance and standards
│   ├── propagate_claude_config.py     # Claude config sync
│   ├── propagate_guidelines.sh        # Guidelines sync
│   ├── propagate_interactive_mode.sh  # Interactive mode
│   ├── setup_compliance.sh            # Initial setup
│   ├── install_compliance_hooks.sh    # Git hooks
│   └── verify_compliance.sh           # Verification
│
├── connection/              # Remote connection tools
│   ├── connect-workspace-linux.sh     # Linux SSH
│   ├── connect-workspace-windows.ps1  # Windows SSH
│   ├── connect-workspace-tailscale.sh # Tailscale (Bash)
│   ├── connect-workspace-tailscale.ps1 # Tailscale (PS)
│   ├── sync-tabby-linux.sh            # Tabby (Linux)
│   └── sync-tabby-windows.ps1         # Tabby (Windows)
│
├── development/             # Development tools
│   ├── install_factory_ai.sh          # Factory.ai installer
│   ├── refactor-analysis.sh           # Code analysis
│   └── droid                          # Droid CLI wrapper
│
└── system/                  # System configuration
    ├── sync                           # Workspace sync
    └── setup_xrdp.sh                  # Remote desktop
```

---

## Navigation Flows

### Example 1: Configure and Clone Repositories

```
./scripts/workspace
  ↓
Main Menu → Select: 1 (Repository Management)
  ↓
Repository Management → Select: 2 (Configure Repository URLs)
  ↓
[Configure URLs interactively]
  ↓
Repository Management → Select: 1 (Repository Sync Manager)
  ↓
Repository Sync → Navigate: Main → Repo Ops → Clone → All
  ↓
[Clone operation executes]
  ↓
Back to main menus
```

### Example 2: Setup Compliance

```
./scripts/workspace
  ↓
Main Menu → Select: 2 (Compliance & Standards)
  ↓
Compliance Menu → Select: 2 (Compliance Enforcement)
  ↓
Enforcement Menu → Select: 1 (Setup Compliance)
  ↓
[Initial compliance setup]
  ↓
Enforcement Menu → Select: 2 (Install Compliance Hooks)
  ↓
[Hooks installed]
  ↓
Back to verify with option 3
```

### Example 3: Refactor Analysis

```
./scripts/workspace
  ↓
Main Menu → Select: 4 (Development Tools)
  ↓
Development Menu → Select: 2 (Refactor Analysis)
  ↓
[Analysis runs, generates reports in .refactor-reports/]
  ↓
Review results
```

---

## Command Reference

### Interactive Mode (Recommended for First-Time Users)

```bash
# Launch workspace management console
./scripts/workspace

# Navigate menus with number keys
# Press 0 to go back
# Press Ctrl+C to exit at any time
```

### Direct Command Mode (For Scripts and Automation)

```bash
# Repository operations
./repository_sync list all
./repository_sync clone work
./repository_sync commit all -m "Update dependencies"
./repository_sync push all
./repository_sync sync personal -m "End of day sync"

# Branch operations
./repository_sync branches all
./repository_sync fetch-branches work
./repository_sync sync-main all
./repository_sync switch work feature-branch

# Compliance operations
./scripts/compliance/propagate_claude_config.py
./scripts/compliance/verify_compliance.sh

# Development tools
./scripts/development/refactor-analysis.sh
./scripts/development/droid --help

# System operations
./scripts/system/sync
./scripts/repository/configure_repos.sh
```

---

## Integration

### With Repository Sync

The workspace CLI integrates seamlessly with the repository_sync tool:

- **Menu access:** Navigate to "Repository Management → Repository Sync Manager"
- **Direct access:** `./repository_sync` (from workspace root)
- **Dual interface:** Both interactive menu and command-based modes available

### With Compliance System

Enforces standards across all repositories:

- **Propagation:** Automatically sync configurations to all repos
- **Hooks:** Git hooks for pre-commit validation
- **Verification:** Continuous compliance monitoring

### With Development Tools

AI-assisted development workflow:

- **Factory.ai:** Droid-based code generation
- **Refactor Analysis:** Automated code quality checks
- **Integration:** Works with SPARC methodology

---

## Best Practices

### For Interactive Use
1. **Start with configuration:** Configure repository URLs first
2. **Use menus for learning:** Interactive menus help discover features
3. **View help when stuck:** Help menu (option 6) provides guidance
4. **Check system info:** View statistics and available tools

### For Automation
1. **Use direct commands:** Faster for scripts and automation
2. **Command-based interface:** `./repository_sync <command> <scope>`
3. **Script paths:** Direct access via `./scripts/<category>/<script>`
4. **Error handling:** Check exit codes for automation

### For Team Collaboration
1. **Setup compliance first:** Ensure standards are enforced
2. **Propagate configurations:** Keep all repos synchronized
3. **Use same structure:** Consistent organization across team
4. **Document workflows:** Share navigation flows for common tasks

---

## Troubleshooting

### Menu Navigation Issues

**Problem:** Menu doesn't display correctly
```bash
# Check terminal supports ANSI colors
echo $TERM

# Run with basic terminal
TERM=xterm ./scripts/workspace
```

**Problem:** Script not found
```bash
# Verify workspace root
pwd

# Should be: /mnt/github/workspace-hub
# If not, cd to workspace root first
```

### Script Execution Errors

**Problem:** Permission denied
```bash
# Make scripts executable
chmod +x ./scripts/workspace
chmod +x ./scripts/*/*.sh
chmod +x ./scripts/*/*.py
```

**Problem:** Script not found in reorganized structure
```bash
# Check new locations:
ls -R ./scripts/

# Use workspace menu to navigate
./scripts/workspace
```

### Repository Configuration Issues

**Problem:** No repository URLs configured
```bash
# Run configuration helper
./scripts/repository/configure_repos.sh

# Or use menu: Repository Management → Configure Repository URLs
```

---

## Support & Resources

### Documentation
- **Main README:** `README.md`
- **Repository Sync:** `docs/REPOSITORY_SYNC.md`
- **Menu Structure:** `docs/CLI_MENU_STRUCTURE.md`
- **Visual Guide:** `docs/MENU_VISUAL_GUIDE.md`
- **This Document:** `docs/WORKSPACE_CLI.md`

### Getting Help
```bash
# Help menu in workspace CLI
./scripts/workspace → Select: 6 (Help & Documentation)

# Repository sync help
./repository_sync help

# Quick start guide
./scripts/workspace → Help & Documentation → Quick Start Guide
```

### Command Reference
```bash
# Available commands
./scripts/workspace → Help & Documentation → Available Commands

# Individual script help
./scripts/<category>/<script> --help
```

---

## Version History

- **v1.0.0** (2025-10-26): Initial unified workspace CLI
  - Created 3-level menu system
  - Reorganized scripts into categories
  - Integrated all workspace tools
  - Added comprehensive help system

---

**Unified workspace management for enhanced productivity! 🚀**
