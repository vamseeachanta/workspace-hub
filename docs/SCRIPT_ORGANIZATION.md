# Script Organization Reference

> Quick reference for workspace-hub script locations and categories
>
> Version: 1.0.0
> Last Updated: 2025-10-26

## Overview

All scripts have been reorganized into 5 logical categories for better maintainability and discoverability. This document provides a quick reference for finding and using scripts.

---

## Category Structure

| Category | Directory | Purpose | Script Count |
|----------|-----------|---------|--------------|
| **Repository** | `scripts/repository/` | Repository management and configuration | 2 |
| **Compliance** | `scripts/compliance/` | Standards enforcement and propagation | 6 |
| **Connection** | `scripts/connection/` | Remote access and terminal sync | 6 |
| **Development** | `scripts/development/` | AI tools and code quality | 3 |
| **System** | `scripts/system/` | System setup and workspace sync | 2 |

**Total Scripts:** 19 organized scripts

---

## Repository Management

**Location:** `scripts/repository/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `configure_repos.sh` | Configure repository URLs | `./scripts/repository/configure_repos.sh` |
| `check_all_status.sh` | Quick status check | `./scripts/repository/check_all_status.sh` |

**Related Tools:**
- `scripts/repository_sync` - Main multi-repo git operations tool

**Menu Access:**
```
./scripts/workspace → Repository Management
```

---

## Compliance & Standards

**Location:** `scripts/compliance/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `propagate_claude_config.py` | Sync CLAUDE.md to all repos | `python3 ./scripts/compliance/propagate_claude_config.py` |
| `propagate_guidelines.sh` | Sync AI usage guidelines | `./scripts/compliance/propagate_guidelines.sh` |
| `propagate_interactive_mode.sh` | Enable question-asking mode | `./scripts/compliance/propagate_interactive_mode.sh` |
| `setup_compliance.sh` | Initial compliance setup | `./scripts/compliance/setup_compliance.sh` |
| `install_compliance_hooks.sh` | Install git hooks | `./scripts/compliance/install_compliance_hooks.sh` |
| `verify_compliance.sh` | Verify compliance status | `./scripts/compliance/verify_compliance.sh` |

**Menu Access:**
```
./scripts/workspace → Compliance & Standards
```

**Workflow:**
1. Setup compliance: `setup_compliance.sh`
2. Install hooks: `install_compliance_hooks.sh`
3. Propagate standards: Use propagation tools
4. Verify: `verify_compliance.sh`

---

## Remote Connection

**Location:** `scripts/connection/`

### Linux/Mac Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `connect-workspace-linux.sh` | SSH connection (Linux) | `./scripts/connection/connect-workspace-linux.sh` |
| `connect-workspace-tailscale.sh` | Tailscale connection (Bash) | `./scripts/connection/connect-workspace-tailscale.sh` |
| `sync-tabby-linux.sh` | Sync Tabby terminal config | `./scripts/connection/sync-tabby-linux.sh` |

### Windows Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `connect-workspace-windows.ps1` | SSH connection (PowerShell) | `.\scripts\connection\connect-workspace-windows.ps1` |
| `connect-workspace-tailscale.ps1` | Tailscale connection (PowerShell) | `.\scripts\connection\connect-workspace-tailscale.ps1` |
| `sync-tabby-windows.ps1` | Sync Tabby terminal config | `.\scripts\connection\sync-tabby-windows.ps1` |

**Menu Access:**
```
./scripts/workspace → Remote Connection Tools
```

---

## Development Tools

**Location:** `scripts/development/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `install_factory_ai.sh` | Install Factory.ai | `./scripts/development/install_factory_ai.sh` |
| `refactor-analysis.sh` | Code quality analysis | `./scripts/development/refactor-analysis.sh` |
| `droid` | Factory.ai droid CLI | `./scripts/development/droid [args]` |

**Menu Access:**
```
./scripts/workspace → Development Tools
```

**Analysis Features:**
- Code duplication detection (jscpd)
- Dead code detection (knip)
- Large file identification
- Slow test detection
- Outdated dependencies

**Reports Generated:** `.refactor-reports/`

---

## System Management

**Location:** `scripts/system/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `sync` | Full workspace synchronization | `./scripts/system/sync` |
| `setup_xrdp.sh` | Remote desktop setup | `./scripts/system/setup_xrdp.sh` |

**Menu Access:**
```
./scripts/workspace → System Setup & Configuration
```

**Sync Components:**
- Git repositories
- MCP servers
- UV environment
- NPM packages
- Agent configurations

---

## Main Entry Points

| Tool | Location | Purpose | Interface |
|------|----------|---------|-----------|
| **workspace** | `./scripts/workspace` | Unified management console | Interactive 3-level menus |
| **repository_sync** | `./scripts/repository_sync` | Multi-repo git operations | Interactive menu + CLI |

---

## Quick Reference Commands

### Interactive Menus
```bash
# Main workspace console
./scripts/workspace

# Repository sync manager
./scripts/repository_sync
```

### Direct Command Access
```bash
# Repository management
./scripts/repository/configure_repos.sh
./scripts/repository_sync list all

# Compliance
./scripts/compliance/verify_compliance.sh
./scripts/compliance/propagate_claude_config.py

# Development
./scripts/development/refactor-analysis.sh

# System
./scripts/system/sync
```

---

## Migration Guide (Old → New Paths)

| Old Location | New Location | Category |
|--------------|--------------|----------|
| `scripts/configure_repos.sh` | `scripts/repository/configure_repos.sh` | Repository |
| `scripts/bash/check_all_status.sh` | `scripts/repository/check_all_status.sh` | Repository |
| `scripts/propagate_claude_config.py` | `scripts/compliance/propagate_claude_config.py` | Compliance |
| `scripts/propagate_guidelines.sh` | `scripts/compliance/propagate_guidelines.sh` | Compliance |
| `scripts/propagate_interactive_mode.sh` | `scripts/compliance/propagate_interactive_mode.sh` | Compliance |
| `scripts/setup_compliance.sh` | `scripts/compliance/setup_compliance.sh` | Compliance |
| `scripts/install_compliance_hooks.sh` | `scripts/compliance/install_compliance_hooks.sh` | Compliance |
| `scripts/verify_compliance.sh` | `scripts/compliance/verify_compliance.sh` | Compliance |
| `scripts/connect-workspace-linux.sh` | `scripts/connection/connect-workspace-linux.sh` | Connection |
| `scripts/connect-workspace-windows.ps1` | `scripts/connection/connect-workspace-windows.ps1` | Connection |
| `scripts/connect-workspace-tailscale.sh` | `scripts/connection/connect-workspace-tailscale.sh` | Connection |
| `scripts/connect-workspace-tailscale.ps1` | `scripts/connection/connect-workspace-tailscale.ps1` | Connection |
| `scripts/sync-tabby-linux.sh` | `scripts/connection/sync-tabby-linux.sh` | Connection |
| `scripts/sync-tabby-windows.ps1` | `scripts/connection/sync-tabby-windows.ps1` | Connection |
| `scripts/install_factory_ai.sh` | `scripts/development/install_factory_ai.sh` | Development |
| `scripts/refactor-analysis.sh` | `scripts/development/refactor-analysis.sh` | Development |
| `scripts/droid` | `scripts/development/droid` | Development |
| `scripts/sync` | `scripts/system/sync` | System |
| `scripts/bash/setup_xrdp.sh` | `scripts/system/setup_xrdp.sh` | System |

---

## Visual Directory Tree

```
workspace-hub/
│
├── scripts/
│   ├── workspace                # Main unified CLI
│   ├── repository_sync          # Repository sync manager
│   │
│   ├── repository/              # Repository management
│   │   ├── configure_repos.sh   # (new) URL configuration
│   │   └── check_all_status.sh  # (moved from bash/)
│   │
│   ├── compliance/              # Compliance & standards
│   │   ├── propagate_claude_config.py     # (moved)
│   │   ├── propagate_guidelines.sh        # (moved)
│   │   ├── propagate_interactive_mode.sh  # (moved)
│   │   ├── setup_compliance.sh            # (moved)
│   │   ├── install_compliance_hooks.sh    # (moved)
│   │   └── verify_compliance.sh           # (moved)
│   │
│   ├── connection/              # Remote connection
│   │   ├── connect-workspace-linux.sh       # (moved)
│   │   ├── connect-workspace-windows.ps1    # (moved)
│   │   ├── connect-workspace-tailscale.sh   # (moved)
│   │   ├── connect-workspace-tailscale.ps1  # (moved)
│   │   ├── sync-tabby-linux.sh              # (moved)
│   │   └── sync-tabby-windows.ps1           # (moved)
│   │
│   ├── development/             # Development tools
│   │   ├── install_factory_ai.sh  # (moved)
│   │   ├── refactor-analysis.sh   # (moved)
│   │   └── droid                  # (moved)
│   │
│   └── system/                  # System management
│       ├── sync                 # (moved)
│       └── setup_xrdp.sh        # (moved from bash/)
│
└── docs/
    ├── WORKSPACE_CLI.md         # (new) Unified CLI documentation
    ├── SCRIPT_ORGANIZATION.md   # (new) This file
    ├── MENU_VISUAL_GUIDE.md     # Interactive menu guide
    ├── CLI_MENU_STRUCTURE.md    # Menu structure tables
    └── REPOSITORY_SYNC.md       # Repository sync documentation
```

---

## Finding Scripts

### By Function

**Need to manage repositories?**
- `scripts/repository/` or `./scripts/workspace → Repository Management`

**Need to enforce standards?**
- `scripts/compliance/` or `./scripts/workspace → Compliance & Standards`

**Need to connect remotely?**
- `scripts/connection/` or `./scripts/workspace → Remote Connection Tools`

**Need development tools?**
- `scripts/development/` or `./scripts/workspace → Development Tools`

**Need system configuration?**
- `scripts/system/` or `./scripts/workspace → System Setup & Configuration`

### By Platform

**Linux/Mac:**
- Use `.sh` scripts directly
- Menu: `./scripts/workspace`

**Windows:**
- Use `.ps1` PowerShell scripts
- Some tools accessible via WSL

---

## Best Practices

### Script Usage
1. **Use menus for discovery:** `./scripts/workspace` helps find features
2. **Use commands for automation:** Direct script paths for scripts
3. **Check categories first:** Know which category contains what you need
4. **Read documentation:** Each category has specific workflows

### Organization Maintenance
1. **Keep categories logical:** Don't mix unrelated scripts
2. **Update paths:** Always use new categorized paths
3. **Document changes:** Update this file when adding scripts
4. **Consistent naming:** Follow existing naming conventions

---

## Support & Documentation

### Primary Documentation
- **Workspace CLI Guide:** `docs/WORKSPACE_CLI.md`
- **Repository Sync Guide:** `docs/REPOSITORY_SYNC.md`
- **This Reference:** `docs/SCRIPT_ORGANIZATION.md`

### Interactive Help
```bash
# Workspace help menu
./scripts/workspace → Help & Documentation

# Repository sync help
./scripts/repository_sync help
```

---

## Version History

- **v1.0.0** (2025-10-26): Initial organized structure
  - Created 5 category system
  - Reorganized all 19 scripts
  - Added unified workspace CLI
  - Created comprehensive documentation

---

**Organized for productivity and maintainability! 🚀**
