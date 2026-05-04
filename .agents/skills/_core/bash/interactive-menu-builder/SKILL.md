---
name: interactive-menu-builder
version: 1.0.0
description: Build multi-level interactive CLI menus with navigation and selection
  for bash scripts
author: workspace-hub
category: _core
tags:
- bash
- menu
- cli
- interactive
- tui
- navigation
platforms:
- linux
- macos
see_also:
- interactive-menu-builder-1-basic-menu-structure
- interactive-menu-builder-2-multi-level-menu-system
- interactive-menu-builder-3-table-display
- interactive-menu-builder-5-confirmation-dialogs
- interactive-menu-builder-1-consistent-navigation
---

# Interactive Menu Builder

## When to Use This Skill

✅ **Use when:**
- Building user-friendly CLI tools
- Need navigation through multiple options
- Complex tools with many sub-commands
- Tools used by humans (not just automation)
- Consolidating multiple scripts into one interface

❌ **Avoid when:**
- Scripts meant for automation/CI
- Simple single-purpose scripts
- When a plain command-line interface is sufficient

## Complete Example: Multi-Level Menu System

Full implementation from workspace CLI:

```bash
#!/bin/bash
# ABOUTME: Complete multi-level menu system
# ABOUTME: Template for workspace-hub style CLI tools

set -e

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

SCRIPT_NAME="$(basename "$0")"
VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

*See sub-skills for full details.*

## Resources

- [Dialog Tool](https://invisible-island.net/dialog/) - TUI dialogs
- [Whiptail](https://en.wikibooks.org/wiki/Bash_Shell_Scripting/Whiptail) - Alternative TUI
- [Gum](https://github.com/charmbracelet/gum) - Modern CLI toolkit

---

## Version History

- **1.0.0** (2026-01-14): Initial release - extracted from workspace-hub CLI tools

## Sub-Skills

- [1. Basic Menu Structure](1-basic-menu-structure/SKILL.md)
- [2. Multi-Level Menu System](2-multi-level-menu-system/SKILL.md)
- [3. Table Display (+1)](3-table-display/SKILL.md)
- [5. Confirmation Dialogs (+1)](5-confirmation-dialogs/SKILL.md)
- [1. Consistent Navigation (+3)](1-consistent-navigation/SKILL.md)
