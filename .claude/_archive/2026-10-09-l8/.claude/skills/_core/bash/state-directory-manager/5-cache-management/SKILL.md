---
name: state-directory-manager-5-cache-management
description: 'Sub-skill of state-directory-manager: 5. Cache Management (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 5. Cache Management (+1)

## 5. Cache Management


Implement caching with expiration:

```bash
#!/bin/bash
# ABOUTME: Cache management with TTL
# ABOUTME: Store and retrieve cached data

CACHE_TTL="${CACHE_TTL:-3600}"  # 1 hour default

# Get cache file path
cache_path() {
    local key="$1"
    local hash=$(echo -n "$key" | md5sum | cut -c1-16)
    echo "$CACHE_DIR/${hash}"
}

# Check if cache is valid
cache_valid() {
    local key="$1"
    local ttl="${2:-$CACHE_TTL}"
    local path=$(cache_path "$key")

    if [[ -f "$path" ]]; then
        local age=$(($(date +%s) - $(stat -c %Y "$path" 2>/dev/null || stat -f %m "$path")))
        [[ $age -lt $ttl ]]
    else
        return 1
    fi
}

# Get from cache
cache_get() {
    local key="$1"
    local ttl="${2:-$CACHE_TTL}"
    local path=$(cache_path "$key")

    if cache_valid "$key" "$ttl"; then
        cat "$path"
        return 0
    fi
    return 1
}

# Set cache
cache_set() {
    local key="$1"
    local value="$2"
    local path=$(cache_path "$key")

    mkdir -p "$CACHE_DIR"
    echo "$value" > "$path"
}

# Delete cache
cache_delete() {
    local key="$1"
    local path=$(cache_path "$key")
    rm -f "$path"
}

# Clear all cache
cache_clear() {
    rm -rf "$CACHE_DIR"/*
}

# Clean expired cache entries
cache_clean() {
    local ttl="${1:-$CACHE_TTL}"
    find "$CACHE_DIR" -type f -mmin "+$((ttl / 60))" -delete 2>/dev/null || true
}

# Usage with automatic caching
get_with_cache() {
    local key="$1"
    local command="$2"
    local ttl="${3:-$CACHE_TTL}"

    if cache_valid "$key" "$ttl"; then
        cache_get "$key"
    else
        local result
        result=$(eval "$command")
        cache_set "$key" "$result"
        echo "$result"
    fi
}

# Example
result=$(get_with_cache "api_response" "curl -s https://api.example.com/data" 300)
```


## 6. Log File Management


Manage logs with rotation:

```bash
#!/bin/bash
# ABOUTME: Log file management with rotation
# ABOUTME: Automatic cleanup of old logs

LOG_FILE="$LOG_DIR/app.log"
LOG_MAX_SIZE=$((10 * 1024 * 1024))  # 10MB
LOG_MAX_FILES=5

# Initialize logging
init_logging() {
    mkdir -p "$LOG_DIR"
    touch "$LOG_FILE"
}

# Write to log
log_to_file() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] $level: $message" >> "$LOG_FILE"

    # Check if rotation needed
    maybe_rotate_logs
}

# Rotate logs if needed
maybe_rotate_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        local size=$(stat -c %s "$LOG_FILE" 2>/dev/null || stat -f %z "$LOG_FILE")

        if [[ $size -gt $LOG_MAX_SIZE ]]; then
            rotate_logs
        fi
    fi
}

# Perform log rotation
rotate_logs() {
    # Remove oldest
    rm -f "${LOG_FILE}.${LOG_MAX_FILES}"

    # Shift existing
    for ((i=LOG_MAX_FILES-1; i>=1; i--)); do
        if [[ -f "${LOG_FILE}.$i" ]]; then
            mv "${LOG_FILE}.$i" "${LOG_FILE}.$((i+1))"
        fi
    done

    # Rotate current
    if [[ -f "$LOG_FILE" ]]; then
        mv "$LOG_FILE" "${LOG_FILE}.1"
        touch "$LOG_FILE"
    fi
}

# Clean old logs
clean_old_logs() {
    local days="${1:-30}"
    find "$LOG_DIR" -name "*.log*" -mtime "+$days" -delete 2>/dev/null || true
}

# View recent logs
tail_logs() {
    local lines="${1:-50}"
    tail -n "$lines" "$LOG_FILE"
}

# Search logs
search_logs() {
    local pattern="$1"
    grep -h "$pattern" "$LOG_DIR"/*.log* 2>/dev/null | tail -100
}
```
