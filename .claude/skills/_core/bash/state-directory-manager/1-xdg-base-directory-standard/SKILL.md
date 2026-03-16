---
name: state-directory-manager-1-xdg-base-directory-standard
description: 'Sub-skill of state-directory-manager: 1. XDG Base Directory Standard
  (+2).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. XDG Base Directory Standard (+2)

## 1. XDG Base Directory Standard


Follow the XDG specification for directory locations:

```bash
#!/bin/bash
# ABOUTME: XDG Base Directory compliant state management
# ABOUTME: Cross-platform directory locations

# XDG Base Directories with fallbacks
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

# Application-specific directories
APP_NAME="my-tool"
CONFIG_DIR="$XDG_CONFIG_HOME/$APP_NAME"
DATA_DIR="$XDG_DATA_HOME/$APP_NAME"
STATE_DIR="$XDG_STATE_HOME/$APP_NAME"
CACHE_DIR="$XDG_CACHE_HOME/$APP_NAME"
LOG_DIR="$STATE_DIR/logs"

# Initialize directories
init_directories() {
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$STATE_DIR"
    mkdir -p "$CACHE_DIR"
    mkdir -p "$LOG_DIR"
}
```


## 2. Workspace-Hub Pattern


Alternative using home directory (from workspace-hub scripts):

```bash
#!/bin/bash
# ABOUTME: Workspace-hub style state directory management
# ABOUTME: Simple $HOME/.app-name pattern

APP_NAME="workspace-hub"
APP_DIR="${HOME}/.${APP_NAME}"

# Directory structure
CONFIG_DIR="$APP_DIR/config"
DATA_DIR="$APP_DIR/data"
LOGS_DIR="$APP_DIR/logs"
CACHE_DIR="$APP_DIR/cache"
TEMP_DIR="$APP_DIR/tmp"

# Initialize with proper permissions
init_app_dirs() {
    local dirs=("$CONFIG_DIR" "$DATA_DIR" "$LOGS_DIR" "$CACHE_DIR" "$TEMP_DIR")

    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            chmod 700 "$dir"  # Private by default
        fi
    done
}

# Clean old temp files
clean_temp() {
    find "$TEMP_DIR" -type f -mtime +1 -delete 2>/dev/null || true
}
```


## 3. Configuration File Management


Read and write configuration files:

```bash
#!/bin/bash
# ABOUTME: Configuration file management
# ABOUTME: Key-value pairs with defaults

CONFIG_FILE="$CONFIG_DIR/config"

# Default configuration
declare -A DEFAULT_CONFIG=(
    ["parallel_workers"]="5"
    ["log_level"]="INFO"
    ["auto_sync"]="true"
    ["timeout"]="30"
)

# Initialize config with defaults
init_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        {
            echo "# Configuration for $APP_NAME"
            echo "# Generated: $(date)"
            echo ""
            for key in "${!DEFAULT_CONFIG[@]}"; do
                echo "${key}=${DEFAULT_CONFIG[$key]}"
            done
        } > "$CONFIG_FILE"
    fi
}

# Read config value
get_config() {
    local key="$1"
    local default="${2:-${DEFAULT_CONFIG[$key]:-}}"

    if [[ -f "$CONFIG_FILE" ]]; then
        local value
        value=$(grep "^${key}=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2-)
        echo "${value:-$default}"
    else
        echo "$default"
    fi
}

# Write config value
set_config() {
    local key="$1"
    local value="$2"

    init_config

    if grep -q "^${key}=" "$CONFIG_FILE" 2>/dev/null; then
        # Update existing
        sed -i "s|^${key}=.*|${key}=${value}|" "$CONFIG_FILE"
    else
        # Add new
        echo "${key}=${value}" >> "$CONFIG_FILE"
    fi
}

# Load all config into associative array
load_config() {
    declare -gA CONFIG

    # Start with defaults
    for key in "${!DEFAULT_CONFIG[@]}"; do
        CONFIG[$key]="${DEFAULT_CONFIG[$key]}"
    done

    # Override with file values
    if [[ -f "$CONFIG_FILE" ]]; then
        while IFS='=' read -r key value; do
            [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
            CONFIG[$key]="$value"
        done < "$CONFIG_FILE"
    fi
}

# Usage
init_config
load_config
echo "Parallel workers: ${CONFIG[parallel_workers]}"
set_config "parallel_workers" "10"
```
