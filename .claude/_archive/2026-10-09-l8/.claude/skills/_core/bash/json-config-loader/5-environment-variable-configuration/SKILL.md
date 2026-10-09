---
name: json-config-loader-5-environment-variable-configuration
description: 'Sub-skill of json-config-loader: 5. Environment Variable Configuration.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 5. Environment Variable Configuration

## 5. Environment Variable Configuration


Load configuration with environment variable overrides:

```bash
#!/bin/bash
# ABOUTME: Configuration with environment variable overrides
# ABOUTME: File config < Environment variable precedence

declare -A APP_CONFIG

# Load config with env override support
load_config_with_env() {
    local file="$1"
    local prefix="${2:-APP_}"  # Environment variable prefix

    # First load from file
    if [[ -f "$file" ]]; then
        while IFS= read -r line || [[ -n "$line" ]]; do
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ -z "${line// /}" ]] && continue

            if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
                local key="${BASH_REMATCH[1]}"
                local value="${BASH_REMATCH[2]}"

                key="${key#"${key%%[![:space:]]*}"}"
                key="${key%"${key##*[![:space:]]}"}"

                APP_CONFIG["$key"]="$value"
            fi
        done < "$file"
    fi

    # Override with environment variables
    for key in "${!APP_CONFIG[@]}"; do
        local env_key="${prefix}${key^^}"  # Convert to UPPER_CASE
        env_key="${env_key//-/_}"          # Replace - with _

        if [[ -v "$env_key" ]]; then
            APP_CONFIG["$key"]="${!env_key}"
        fi
    done
}

# Check required config keys
require_config() {
    local missing=()

    for key in "$@"; do
        if [[ -z "${APP_CONFIG[$key]:-}" ]]; then
            missing+=("$key")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Error: Missing required configuration:" >&2
        printf "  - %s\n" "${missing[@]}" >&2
        return 1
    fi

    return 0
}

# Get config with type conversion
config_string() {
    local key="$1"
    local default="${2:-}"
    echo "${APP_CONFIG[$key]:-$default}"
}

config_int() {
    local key="$1"
    local default="${2:-0}"
    local value="${APP_CONFIG[$key]:-$default}"

    if [[ "$value" =~ ^-?[0-9]+$ ]]; then
        echo "$value"
    else
        echo "$default"
    fi
}

config_bool() {
    local key="$1"
    local default="${2:-false}"
    local value="${APP_CONFIG[$key]:-$default}"

    case "${value,,}" in
        true|yes|1|on) echo "true" ;;
        false|no|0|off) echo "false" ;;
        *) echo "$default" ;;
    esac
}

# Usage
load_config_with_env "app.conf" "MYAPP_"

# Check required keys
require_config "api_key" "database_url" || exit 1

# Access with type conversion
PORT=$(config_int "port" 8080)
DEBUG=$(config_bool "debug" false)
API_KEY=$(config_string "api_key")

echo "Starting on port $PORT (debug: $DEBUG)"
```
