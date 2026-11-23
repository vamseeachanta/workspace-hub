---
name: json-config-loader-6-yaml-configuration-via-yq
description: 'Sub-skill of json-config-loader: 6. YAML Configuration (via yq).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 6. YAML Configuration (via yq)

## 6. YAML Configuration (via yq)


Parse YAML files when yq is available:

```bash
#!/bin/bash
# ABOUTME: YAML configuration parsing with yq
# ABOUTME: Falls back to jq for JSON subset of YAML

# Check for yaml parser
get_yaml_parser() {
    if command -v yq &> /dev/null; then
        echo "yq"
    elif command -v jq &> /dev/null; then
        echo "jq"  # Can parse YAML's JSON subset
    else
        echo "none"
    fi
}

# Load YAML config
load_yaml_config() {
    local file="$1"
    local parser
    parser=$(get_yaml_parser)

    if [[ ! -f "$file" ]]; then
        echo "{}"
        return 1
    fi

    case "$parser" in
        yq)
            yq -o=json "$file" 2>/dev/null || echo "{}"
            ;;
        jq)
            # Try to parse as JSON (YAML subset)
            jq '.' "$file" 2>/dev/null || echo "{}"
            ;;
        *)
            echo "Error: No YAML parser available (install yq or jq)" >&2
            echo "{}"
            return 1
            ;;
    esac
}

# Get YAML value (returns as JSON for jq processing)
yaml_get() {
    local file="$1"
    local path="$2"
    local default="${3:-}"

    local parser
    parser=$(get_yaml_parser)

    local value
    case "$parser" in
        yq)
            value=$(yq -r "$path // \"$default\"" "$file" 2>/dev/null)
            ;;
        jq)
            value=$(jq -r "$path // \"$default\"" "$file" 2>/dev/null)
            ;;
        *)
            value="$default"
            ;;
    esac

    if [[ -z "$value" || "$value" == "null" ]]; then
        echo "$default"
    else
        echo "$value"
    fi
}

# Usage
CONFIG_FILE="config.yaml"

# Load entire config as JSON
CONFIG_JSON=$(load_yaml_config "$CONFIG_FILE")

# Or get specific values
DB_HOST=$(yaml_get "$CONFIG_FILE" '.database.host' 'localhost')
DB_PORT=$(yaml_get "$CONFIG_FILE" '.database.port' '5432')

echo "Database: $DB_HOST:$DB_PORT"
```
