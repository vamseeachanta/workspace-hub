---
name: bash-cli-framework
version: 1.0.0
description: Universal bash CLI patterns for colors, logging, headers, and error handling
author: workspace-hub
category: _core
tags:
- bash
- cli
- colors
- logging
- framework
- scripting
platforms:
- linux
- macos
see_also:
- bash-cli-framework-1-color-definitions
- bash-cli-framework-5-error-handling
- bash-cli-framework-1-always-use-set-e
---

# Bash Cli Framework

## When to Use This Skill

✅ **Use when:**
- Building new bash CLI tools or scripts
- Adding consistent output formatting to existing scripts
- Need standardized error handling and logging
- Creating user-friendly interactive scripts
- Building tools that will be used across multiple repositories

❌ **Avoid when:**
- Simple one-liner scripts
- Scripts that don't produce user-facing output
- When Python/Node CLI frameworks are more appropriate

## Complete Example

A complete script using all framework components:

```bash
#!/bin/bash
# ABOUTME: Example script demonstrating bash-cli-framework usage
# ABOUTME: Template for new CLI tools in workspace-hub

set -e

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'


*See sub-skills for full details.*

## Integration with workspace-hub

This framework is used across all workspace-hub scripts:
- `scripts/monitoring/suggest_model.sh`
- `scripts/monitoring/check_claude_usage.sh`
- `scripts/workspace`
- `scripts/repository_sync`

## Resources

- [Bash Best Practices](https://mywiki.wooledge.org/BashGuide/Practices)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [ShellCheck](https://www.shellcheck.net/) - Static analysis tool

---

## Version History

- **1.0.0** (2026-01-14): Initial release - extracted from workspace-hub scripts

## Sub-Skills

- [1. Color Definitions (+3)](1-color-definitions/SKILL.md)
- [5. Error Handling (+1)](5-error-handling/SKILL.md)
- [1. Always Use `set -e` (+4)](1-always-use-set-e/SKILL.md)
