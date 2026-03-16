---
name: cli-productivity
version: 1.0.0
description: Essential CLI tools and shell productivity patterns for efficient terminal
  workflows
author: workspace-hub
category: operations
capabilities:
- Shell aliases and functions
- Modern CLI tools (jq, fzf, ripgrep, fd, bat, exa)
- Pipeline patterns and data transformation
- Fuzzy finding and interactive selection
- History management and shell optimization
- Integration workflows between tools
tools:
- jq
- fzf
- ripgrep
- fd
- bat
- exa
- zoxide
- starship
- tmux
tags:
- cli
- shell
- productivity
- bash
- zsh
- terminal
- tools
platforms:
- linux
- macos
related_skills:
- docker
- git-advanced
- bash-cli-framework
requires: []
see_also:
- cli-productivity-1-jq-json-processing
- cli-productivity-3-ripgrep-rg-fast-search
- cli-productivity-5-bat-better-cat
- cli-productivity-8-shell-aliases-and-functions
- cli-productivity-1-complete-shell-configuration
- cli-productivity-3-interactive-script-template
- cli-productivity-1-tool-selection-guidelines
- cli-productivity-common-issues
scripts_exempt: true
---

# Cli Productivity

## When to Use This Skill

### USE when:

- Building efficient terminal workflows
- Processing text and JSON data
- Searching codebases quickly
- Navigating file systems efficiently
- Automating repetitive tasks
- Creating shell functions and aliases
- Building interactive scripts
### DON'T USE when:

- GUI-based workflows are more appropriate
- Processing binary data (use specialized tools)
- Complex data analysis (use Python/Pandas)
- Tasks requiring visual feedback

## Prerequisites

### Installation

**macOS (Homebrew):**
```bash
# Essential modern tools
brew install jq           # JSON processor
brew install fzf          # Fuzzy finder
brew install ripgrep      # Fast grep (rg)
brew install fd           # Fast find
brew install bat          # Better cat
brew install exa          # Better ls (or eza)
brew install zoxide       # Smart cd

*See sub-skills for full details.*

## Version History

- **1.0.0** (2026-01-17): Initial release
  - Core CLI tools coverage (jq, fzf, ripgrep, fd, bat, exa)
  - Shell aliases and functions
  - Pipeline patterns
  - Integration examples
  - Shell configuration templates

---

**Use this skill to build efficient, productive terminal workflows with modern CLI tools!**

## Sub-Skills

- [1. jq - JSON Processing (+1)](1-jq-json-processing/SKILL.md)
- [3. ripgrep (rg) - Fast Search (+1)](3-ripgrep-rg-fast-search/SKILL.md)
- [5. bat - Better cat (+2)](5-bat-better-cat/SKILL.md)
- [8. Shell Aliases and Functions](8-shell-aliases-and-functions/SKILL.md)
- [1. Complete Shell Configuration (+1)](1-complete-shell-configuration/SKILL.md)
- [3. Interactive Script Template](3-interactive-script-template/SKILL.md)
- [1. Tool Selection Guidelines (+2)](1-tool-selection-guidelines/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
