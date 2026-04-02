---
name: vscode-extensions
version: 1.0.0
description: VS Code productivity optimization with essential extensions, settings
  sync, profiles, keybindings, snippets, and workspace configuration
author: workspace-hub
category: operations
type: skill
capabilities:
- extension_management
- settings_configuration
- profile_management
- keybinding_customization
- snippet_creation
- workspace_settings
- task_automation
- debugging_configuration
- theme_customization
- remote_development
tools:
- code
- code-insiders
- codium
tags:
- vscode
- ide
- extensions
- productivity
- editor
- development
- settings
- profiles
platforms:
- linux
- macos
- windows
related_skills:
- cli-productivity
- git-advanced
- docker
requires: []
scripts_exempt: true
---

# Vscode Extensions

## When to Use This Skill

### USE when:

- Setting up a new development environment
- Optimizing VS Code for specific languages/frameworks
- Creating consistent team configurations
- Building custom snippets and tasks
- Configuring debugging for complex applications
- Managing multiple project profiles
- Automating repetitive editor tasks
### DON'T USE when:

- Need full IDE features (use JetBrains IDEs)
- Working exclusively in terminal (use vim/neovim)
- Resource-constrained environments (use lighter editors)
- Pair programming with different editors (standardize first)

## Prerequisites

### Installation

```bash
# macOS
brew install --cask visual-studio-code

# Linux (Ubuntu/Debian)
sudo snap install code --classic
# Or download from https://code.visualstudio.com/

# Windows
winget install Microsoft.VisualStudioCode

*See sub-skills for full details.*
### CLI Extension Management

```bash
# List installed extensions
code --list-extensions

# Install extension
code --install-extension ms-python.python

# Uninstall extension
code --uninstall-extension extension-id


*See sub-skills for full details.*

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive VS Code configuration |

## Resources

- [VS Code Documentation](https://code.visualstudio.com/docs)
- [VS Code Keybindings Reference](https://code.visualstudio.com/docs/getstarted/keybindings)
- [Extension Marketplace](https://marketplace.visualstudio.com/vscode)
- [Snippet Guide](https://code.visualstudio.com/docs/editor/userdefinedsnippets)
- [Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)
- [Debugging Guide](https://code.visualstudio.com/docs/editor/debugging)

---

*This skill provides production-ready VS Code configurations for maximum developer productivity across multiple languages and frameworks.*

## Sub-Skills

- [1. Essential Extensions by Category](1-essential-extensions-by-category/SKILL.md)
- [2. Settings Configuration](2-settings-configuration/SKILL.md)
- [3. Language-Specific Settings](3-language-specific-settings/SKILL.md)
- [4. Keybindings Configuration](4-keybindings-configuration/SKILL.md)
- [5. Custom Snippets](5-custom-snippets/SKILL.md)
- [6. Workspace Configuration](6-workspace-configuration/SKILL.md)
- [7. Profile Management](7-profile-management/SKILL.md)
- [Git Workflow Integration (+1)](git-workflow-integration/SKILL.md)
- [1. Extension Management (+2)](1-extension-management/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
