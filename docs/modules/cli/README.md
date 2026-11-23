# CLI & Tools Documentation

This directory contains all documentation related to command-line interfaces, scripts, and tools.

## Contents

| File | Description |
|------|-------------|
| [WORKSPACE_CLI.md](WORKSPACE_CLI.md) | Main workspace CLI guide |
| [CLI_MENU_STRUCTURE.md](CLI_MENU_STRUCTURE.md) | CLI menu organization |
| [MENU_VISUAL_GUIDE.md](MENU_VISUAL_GUIDE.md) | Visual guide to menus |
| [SCRIPT_ORGANIZATION.md](SCRIPT_ORGANIZATION.md) | Script folder structure |
| [REPOSITORY_SYNC.md](REPOSITORY_SYNC.md) | Repository synchronization tools |

## Quick Start

### Workspace CLI

```bash
# Launch interactive workspace menu
./scripts/workspace

# Main menu options:
# 1) Git Repositories - Sync all or specific repos
# 2) MCP Servers - Install MCP servers
# 3) UV Environment - Setup Python package manager
# 4) NPM Packages - Install global npm packages
# 5) Agent Configurations - Manage agent configs
# 9) Sync Everything - Full workspace sync
```

### Repository Sync

```bash
# Pull all repositories
./scripts/repository_sync pull all

# Check status of all repos
./scripts/repository_sync status

# Push changes across repos
./scripts/repository_sync push all
```

### Script Organization

Scripts are organized by category:

```
scripts/
├── workspace           # Main CLI entry point
├── repository_sync     # Repo sync operations
├── compliance/         # Compliance checking
├── config/             # Configuration tools
├── git/                # Git operations
├── python/             # Python utilities
└── sync/               # Sync operations
```

## Key Principles

- **Use scripts over direct commands** - Scripts provide tested, validated workflows
- **Check script availability first** - Before manual operations
- **Single command entry points** - Simple, reproducible execution

## Related Documentation

- [Development Workflow](../workflow/) - Overall development process
- [Standards](../standards/) - Script and code standards

---

*Part of the workspace-hub documentation infrastructure*
