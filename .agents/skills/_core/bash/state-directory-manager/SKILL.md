---
name: state-directory-manager
version: 1.0.0
description: Manage persistent state directories with XDG-compliant paths and cleanup
  for bash scripts
author: workspace-hub
category: _core
tags:
- bash
- state
- persistence
- config
- directory
- xdg
platforms:
- linux
- macos
see_also:
- state-directory-manager-1-xdg-base-directory-standard
- state-directory-manager-4-state-file-operations
- state-directory-manager-5-cache-management
- state-directory-manager-best-practices
---

# State Directory Manager

## When to Use This Skill

✅ **Use when:**
- Scripts need to persist data between runs
- Storing user preferences or configuration
- Caching results for performance
- Managing log files with rotation
- Creating portable CLI tools

❌ **Avoid when:**
- One-time scripts that don't need state
- Scripts that should be purely stateless
- When environment variables are sufficient

## Complete Example: State Manager Module

```bash
#!/bin/bash
# ABOUTME: Complete state directory manager
# ABOUTME: Reusable module for bash scripts

# ─────────────────────────────────────────────────────────────────
# State Directory Manager v1.0.0
# ─────────────────────────────────────────────────────────────────

# Application identity (override in your script)
: "${STATE_APP_NAME:=my-app}"

# Directory setup
STATE_BASE_DIR="${HOME}/.${STATE_APP_NAME}"
STATE_CONFIG_DIR="$STATE_BASE_DIR/config"
STATE_DATA_DIR="$STATE_BASE_DIR/data"
STATE_CACHE_DIR="$STATE_BASE_DIR/cache"
STATE_LOG_DIR="$STATE_BASE_DIR/logs"
STATE_TMP_DIR="$STATE_BASE_DIR/tmp"

# File paths
STATE_CONFIG_FILE="$STATE_CONFIG_DIR/config"
STATE_STATE_FILE="$STATE_DATA_DIR/state"
STATE_LOG_FILE="$STATE_LOG_DIR/app.log"


*See sub-skills for full details.*

## Usage in Scripts

```bash
#!/bin/bash
# Your script that uses the state manager

# Set app name before sourcing
STATE_APP_NAME="my-tool"

# Source the state manager
source /path/to/state-manager.sh

# Now use it
state_config_set "api_key" "abc123"
api_key=$(state_config_get "api_key")

state_set "last_run" "$(date -Iseconds)"
state_log "INFO" "Script started"

# Use cache
if ! result=$(state_cache_get "api_response"); then
    result=$(curl -s https://api.example.com/data)
    state_cache_set "api_response" "$result"
fi
```

## Resources

- [XDG Base Directory Spec](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [File Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - extracted from workspace-hub patterns

## Sub-Skills

- [1. XDG Base Directory Standard (+2)](1-xdg-base-directory-standard/SKILL.md)
- [4. State File Operations](4-state-file-operations/SKILL.md)
- [5. Cache Management (+1)](5-cache-management/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
