---
name: json-config-loader-1-keyvalue-configuration-parsing
description: 'Sub-skill of json-config-loader: 1. Key=Value Configuration Parsing
  (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Key=Value Configuration Parsing (+1)

## 1. Key=Value Configuration Parsing


Parse simple key=value configuration files:

```bash
#!/bin/bash
# ABOUTME: Parse key=value configuration files
# ABOUTME: Supports comments, empty lines, and quoted values

CONFIG_FILE="${1:-config.conf}"

# Declare associative array for config
declare -A CONFIG

# Parse configuration file
parse_config() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo "Error: Config file not found: $file" >&2
        return 1
    fi

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// /}" ]] && continue

        # Parse key=value pairs
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"

            # Trim whitespace
            key="${key#"${key%%[![:space:]]*}"}"
            key="${key%"${key##*[![:space:]]}"}"
            value="${value#"${value%%[![:space:]]*}"}"
            value="${value%"${value##*[![:space:]]}"}"

            # Remove surrounding quotes if present
            if [[ "$value" =~ ^\"(.*)\"$ ]] || [[ "$value" =~ ^\'(.*)\'$ ]]; then
                value="${BASH_REMATCH[1]}"
            fi

            CONFIG["$key"]="$value"
        fi
    done < "$file"
}

# Get config value with default
get_config() {
    local key="$1"
    local default="${2:-}"

    echo "${CONFIG[$key]:-$default}"
}

# Check if key exists
has_config() {
    local key="$1"
    [[ -v CONFIG[$key] ]]
}

# Usage
parse_config "$CONFIG_FILE"

# Access values
echo "Database: $(get_config 'database' 'default.db')"
echo "Port: $(get_config 'port' '8080')"

if has_config 'debug'; then
    echo "Debug mode enabled"
fi
```


## 2. JSON Configuration with jq


Load and manipulate JSON configuration:

```bash
#!/bin/bash
# ABOUTME: JSON configuration loading with jq
# ABOUTME: Provides safe defaults and nested value access

# Check jq dependency
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required but not installed" >&2
        echo "Install with: apt install jq (Ubuntu) or brew install jq (Mac)" >&2
        exit 1
    fi
}

# Load JSON config file
load_json_config() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo "{}"
        return 1
    fi

    # Validate JSON
    if ! jq empty "$file" 2>/dev/null; then
        echo "Error: Invalid JSON in $file" >&2
        echo "{}"
        return 1
    fi

    cat "$file"
}

# Get value from JSON with default
json_get() {
    local json="$1"
    local path="$2"
    local default="${3:-}"

    local value
    value=$(echo "$json" | jq -r "$path // empty" 2>/dev/null)

    if [[ -z "$value" || "$value" == "null" ]]; then
        echo "$default"
    else
        echo "$value"
    fi
}

# Get array from JSON
json_get_array() {
    local json="$1"
    local path="$2"

    echo "$json" | jq -r "$path[]? // empty" 2>/dev/null
}

# Check if path exists in JSON
json_has() {
    local json="$1"
    local path="$2"

    local result
    result=$(echo "$json" | jq -e "$path != null" 2>/dev/null)
    [[ "$result" == "true" ]]
}

# Usage example
check_jq

CONFIG_JSON=$(load_json_config "config.json")

# Access nested values
DB_HOST=$(json_get "$CONFIG_JSON" '.database.host' 'localhost')
DB_PORT=$(json_get "$CONFIG_JSON" '.database.port' '5432')
DEBUG=$(json_get "$CONFIG_JSON" '.settings.debug' 'false')

echo "Database: $DB_HOST:$DB_PORT"
echo "Debug: $DEBUG"

# Iterate array values
echo "Enabled features:"
while IFS= read -r feature; do
    echo "  - $feature"
done < <(json_get_array "$CONFIG_JSON" '.features')
```
