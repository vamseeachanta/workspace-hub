---
name: json-config-loader-4-multi-section-ini-parsing
description: 'Sub-skill of json-config-loader: 4. Multi-Section INI Parsing.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 4. Multi-Section INI Parsing

## 4. Multi-Section INI Parsing


Parse INI-style files with sections:

```bash
#!/bin/bash
# ABOUTME: Parse INI-style configuration with sections
# ABOUTME: Supports [section] headers and section.key access

declare -A INI_CONFIG
declare -a INI_SECTIONS=()

parse_ini() {
    local file="$1"
    local current_section="default"

    if [[ ! -f "$file" ]]; then
        echo "Error: INI file not found: $file" >&2
        return 1
    fi

    INI_SECTIONS=("default")

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*[#\;] ]] && continue
        [[ -z "${line// /}" ]] && continue

        # Section header
        if [[ "$line" =~ ^\[([^\]]+)\] ]]; then
            current_section="${BASH_REMATCH[1]}"
            INI_SECTIONS+=("$current_section")
            continue
        fi

        # Key=value within section
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"

            # Trim whitespace
            key="${key#"${key%%[![:space:]]*}"}"
            key="${key%"${key##*[![:space:]]}"}"
            value="${value#"${value%%[![:space:]]*}"}"
            value="${value%"${value##*[![:space:]]}"}"

            # Store as section.key
            INI_CONFIG["${current_section}.${key}"]="$value"
        fi
    done < "$file"
}

# Get INI value
ini_get() {
    local section="$1"
    local key="$2"
    local default="${3:-}"

    echo "${INI_CONFIG["${section}.${key}"]:-$default}"
}

# Get all keys in a section
ini_section_keys() {
    local section="$1"
    local prefix="${section}."

    for key in "${!INI_CONFIG[@]}"; do
        if [[ "$key" == "${prefix}"* ]]; then
            echo "${key#$prefix}"
        fi
    done
}

# List all sections
ini_sections() {
    printf '%s\n' "${INI_SECTIONS[@]}" | sort -u
}

# Usage
parse_ini "settings.ini"

# Access values
DB_HOST=$(ini_get "database" "host" "localhost")
DB_PORT=$(ini_get "database" "port" "5432")
LOG_LEVEL=$(ini_get "logging" "level" "INFO")

echo "Database: $DB_HOST:$DB_PORT"
echo "Log Level: $LOG_LEVEL"

# Iterate section keys
echo "Database settings:"
for key in $(ini_section_keys "database"); do
    echo "  $key = $(ini_get "database" "$key")"
done
```
