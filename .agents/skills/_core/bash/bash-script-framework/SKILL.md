---
name: bash-script-framework
description: Create organized bash script structure with color output, menu systems,
  error handling, and cross-platform support. Standardizes CLI tooling.
version: 1.1.0
category: _core
type: skill
trigger: manual
auto_execute: false
capabilities:
- script_organization
- menu_systems
- color_output
- error_handling
- cross_platform
tools:
- Write
- Bash
- Read
related_skills:
- python-project-template
- yaml-workflow-executor
tags: []
see_also:
- bash-script-framework-example-1-create-new-cli-tool
- bash-script-framework-best-practices
---

# Bash Script Framework

## Quick Start

```bash
# Create script directory structure
/bash-script-framework init

# Create new script with menu
/bash-script-framework new my-script --menu

# Add to existing scripts directory
/bash-script-framework add utility-script
```

## When to Use

**USE when:**
- Creating CLI tools for repository
- Building menu-driven automation
- Standardizing script organization
- Cross-platform script development

**DON'T USE when:**
- Python script is more appropriate
- Simple one-liner needed
- Windows-only environment

> For Windows/Git Bash-compatible scripts, see `_core/bash/cross-platform-compat`.

## Prerequisites

- Bash 4.0+
- Unix-like environment (Linux, macOS, WSL)

## Overview

Creates organized bash scripts following workspace-hub patterns:

1. **Color utilities** - Consistent terminal output
2. **Menu systems** - Multi-level navigation
3. **Error handling** - Proper exit codes
4. **Logging** - Timestamped output
5. **Cross-platform** - Linux/macOS/WSL support

## Directory Structure

```
scripts/
├── workspace                  # Main entry point
├── lib/
│   ├── colors.sh             # Color definitions
│   ├── logging.sh            # Logging utilities
│   ├── menu.sh               # Menu system
│   └── utils.sh              # General utilities
├── bash/
│   ├── git/                  # Git operations
│   └── dev/                  # Development tools
├── python/                   # Python utilities
└── powershell/               # Windows scripts
```

## Core Templates

### 1. Color Library (lib/colors.sh)

```bash
#!/bin/bash
# lib/colors.sh - Color definitions for terminal output
# Source this file: source lib/colors.sh

# Reset
NC='\033[0m'              # No Color / Reset

# Regular Colors
BLACK='\033[0;30m'

*See sub-skills for full details.*
### 2. Logging Library (lib/logging.sh)

```bash
#!/bin/bash
# lib/logging.sh - Logging utilities
# Source this file after colors.sh

# Log levels
LOG_LEVEL_DEBUG=0
LOG_LEVEL_INFO=1
LOG_LEVEL_WARN=2
LOG_LEVEL_ERROR=3

*See sub-skills for full details.*
### 3. Menu System (lib/menu.sh)

```bash
#!/bin/bash
# lib/menu.sh - Menu system utilities
# Source after colors.sh

# Display menu and get selection
show_menu() {
    local title="$1"
    shift
    local options=("$@")

*See sub-skills for full details.*
### 4. Utilities (lib/utils.sh)

```bash
#!/bin/bash
# lib/utils.sh - General utilities

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check required commands

*See sub-skills for full details.*
### 5. Main Script Template

```bash
#!/bin/bash
# scripts/my-tool - Main entry point
# Description: Tool description here

set -e  # Exit on error

# Get script directory and load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/colors.sh"

*See sub-skills for full details.*

## Related Skills

- [python-project-template](../python-project-template/SKILL.md) - Python CLI tools
- [yaml-workflow-executor](../yaml-workflow-executor/SKILL.md) - YAML-driven execution

## References

- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [workspace-hub CLI Standards](../../../docs/modules/cli/WORKSPACE_CLI.md)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - bash script framework with colors, menus, logging, and utilities

## Sub-Skills

- [Example 1: Create New CLI Tool (+1)](example-1-create-new-cli-tool/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
