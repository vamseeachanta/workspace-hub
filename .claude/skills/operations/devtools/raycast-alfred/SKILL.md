---
name: raycast-alfred
version: 1.0.0
description: macOS launcher automation with Raycast extensions (TypeScript/React)
  and Alfred workflows (AppleScript/Python) for keyboard-driven productivity
author: workspace-hub
category: operations
type: skill
capabilities:
- raycast_extensions
- alfred_workflows
- script_commands
- keyboard_shortcuts
- clipboard_management
- snippet_expansion
- file_search
- window_management
- system_commands
- application_integration
tools:
- raycast
- alfred
- typescript
- node
- python
- applescript
tags:
- raycast
- alfred
- macos
- launcher
- automation
- productivity
- scripts
- typescript
- applescript
platforms:
- macos
related_skills:
- cli-productivity
- vscode-extensions
- git-advanced
requires: []
see_also:
- raycast-alfred-headers
- raycast-alfred-6-keyboard-shortcuts-and-snippets
scripts_exempt: true
---

# Raycast Alfred

## When to Use This Skill

### USE when:

- Building quick access tools for developer workflows
- Automating repetitive macOS tasks
- Creating custom search commands
- Building clipboard history managers
- Implementing text snippet expansion
- Creating project launchers and switchers
- Building API query tools
- Automating application control
- Creating custom keyboard shortcuts
- Building team productivity tools
### DON'T USE when:

- Cross-platform automation needed (use shell scripts)
- Server-side automation (use cron/systemd)
- GUI testing automation (use Playwright/Selenium)
- Windows/Linux environments
- Heavy computation tasks (use proper CLI tools)

## Prerequisites

### Raycast Setup

```bash
# Install Raycast
brew install --cask raycast

# Install Node.js (required for extension development)
brew install node

# Install Raycast CLI
npm install -g @raycast/api


*See sub-skills for full details.*
### Alfred Setup

```bash
# Install Alfred (Powerpack required for workflows)
brew install --cask alfred

# Alfred workflow locations
# ~/Library/Application Support/Alfred/Alfred.alfredpreferences/workflows/

# Create workflow via Alfred Preferences > Workflows > + > Blank Workflow

# Workflow components:

*See sub-skills for full details.*
### Development Environment

```bash
# For Raycast TypeScript development
npm install -g typescript @types/node

# For Alfred Python workflows
pip install alfred-workflow  # (legacy, but useful patterns)

# AppleScript tools
brew install --cask script-debugger  # Optional: AppleScript IDE

# Testing tools
brew install jq  # JSON parsing
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with Raycast and Alfred patterns |

## Resources

- [Raycast Developer Documentation](https://developers.raycast.com/)
- [Raycast API Reference](https://developers.raycast.com/api-reference)
- [Alfred Workflow Documentation](https://www.alfredapp.com/help/workflows/)
- [AppleScript Language Guide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/)
- [Raycast Store](https://www.raycast.com/store)
- [Alfred Gallery](https://alfred.app/workflows/)

---

*This skill provides production-ready patterns for macOS launcher automation, enabling keyboard-driven productivity and seamless workflow integration.*

## Sub-Skills

- [1. Raycast Script Commands](1-raycast-script-commands/SKILL.md)
- [2. Raycast TypeScript Extensions](2-raycast-typescript-extensions/SKILL.md)
- [3. Alfred Workflows - AppleScript](3-alfred-workflows-applescript/SKILL.md)
- [4. Alfred Workflows - Python](4-alfred-workflows-python/SKILL.md)
- [5. Raycast Extension - API Integration](5-raycast-extension-api-integration/SKILL.md)
- [Project Switcher Integration](project-switcher-integration/SKILL.md)
- [1. Raycast Extension Development (+2)](1-raycast-extension-development/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)

## Sub-Skills

- [Headers](headers/SKILL.md)
- [6. Keyboard Shortcuts and Snippets](6-keyboard-shortcuts-and-snippets/SKILL.md)
