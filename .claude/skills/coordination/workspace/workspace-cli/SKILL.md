---
name: workspace-cli
description: Use the workspace-hub unified CLI for repository management, compliance,
  development tools, and system configuration. Use for navigating workspace tools
  and executing common operations.
version: 1.1.0
category: coordination
type: skill
capabilities:
- interactive_menu_navigation
- repository_management
- compliance_tools_access
- development_utilities
- system_configuration
tools:
- Bash
- Read
related_skills:
- repo-sync
- compliance-check
- sparc-workflow
requires: []
see_also:
- workspace-cli-direct-script-access
- workspace-cli-main-menu-structure
- workspace-cli-execution-checklist
- workspace-cli-1-repository-management
- workspace-cli-6-help-documentation
- workspace-cli-script-organization
- workspace-cli-daily-development-start
- workspace-cli-menu-display-issues
- workspace-cli-metrics-success-criteria
- workspace-cli-keyboard-navigation
- workspace-cli-with-repository-sync
- workspace-cli-supported-variables
tags: []
---

# Workspace Cli

## Quick Start

```bash
# Launch interactive menu
./scripts/workspace

# Direct repository sync
./scripts/repository_sync status all

# Quick compliance check
./scripts/compliance/verify_compliance.sh
```

## When to Use

- Starting a work session and need quick access to common tools
- Managing multiple repositories with bulk operations
- Running compliance checks across the workspace
- Accessing development tools and refactoring utilities
- Configuring system settings and remote connections

## Prerequisites

- Access to workspace-hub repository
- Bash shell (Linux/macOS/WSL)
- Scripts marked as executable (`chmod +x ./scripts/workspace`)

## Overview

The Workspace CLI provides a unified interface to all workspace-hub management tools. This skill covers navigation, common operations, and integration with other workspace systems.

## References

- [WORKSPACE_CLI.md](../docs/modules/cli/WORKSPACE_CLI.md)
- [REPOSITORY_SYNC.md](../docs/modules/cli/REPOSITORY_SYNC.md)
- [CLI_MENU_STRUCTURE.md](../docs/modules/cli/CLI_MENU_STRUCTURE.md)

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format - added When to Use, Execution Checklist, Error Handling consolidation, Metrics, Integration Points
- **1.0.0** (2024-10-15): Initial release with 6 main categories, script organization, workflows, navigation, troubleshooting

## Sub-Skills

- [Direct Script Access](direct-script-access/SKILL.md)
- [Main Menu Structure](main-menu-structure/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [1. Repository Management (+4)](1-repository-management/SKILL.md)
- [6. Help & Documentation](6-help-documentation/SKILL.md)
- [Script Organization](script-organization/SKILL.md)
- [Daily Development Start (+4)](daily-development-start/SKILL.md)
- [Menu Display Issues (+3)](menu-display-issues/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [Keyboard Navigation (+2)](keyboard-navigation/SKILL.md)
- [With Repository Sync (+3)](with-repository-sync/SKILL.md)
- [Supported Variables (+1)](supported-variables/SKILL.md)
