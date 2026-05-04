---
name: bash-cli-framework-1-color-definitions
description: 'Sub-skill of bash-cli-framework: 1. Color Definitions (+3).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Color Definitions (+3)

## 1. Color Definitions


Standard ANSI color codes for consistent terminal output:

```bash
#!/bin/bash
# ABOUTME: Standard color definitions for CLI output
# ABOUTME: Use these consistently across all workspace-hub scripts

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Bold variants
BOLD='\033[1m'
BOLD_RED='\033[1;31m'
BOLD_GREEN='\033[1;32m'
BOLD_YELLOW='\033[1;33m'
BOLD_BLUE='\033[1;34m'

# Usage examples
echo -e "${GREEN}✓ Success${NC}"
echo -e "${RED}✗ Error${NC}"
echo -e "${YELLOW}⚠ Warning${NC}"
echo -e "${CYAN}ℹ Info${NC}"
```


## 2. Script Header Template


Every script should start with proper identification:

```bash
#!/bin/bash
# ABOUTME: Brief one-line description of what this script does
# ABOUTME: Additional context about usage or dependencies

set -e  # Exit on error

# Script metadata
SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"
```


## 3. Logging Functions


Standardized logging with timestamps and levels:

```bash
#!/bin/bash
# ABOUTME: Logging framework for bash scripts
# ABOUTME: Supports DEBUG, INFO, WARNING, ERROR, CRITICAL levels

# Log file configuration
LOG_FILE="${LOG_FILE:-/tmp/${SCRIPT_NAME}.log}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Log level values
declare -A LOG_LEVELS=(
    ["DEBUG"]=0
    ["INFO"]=1
    ["WARNING"]=2
    ["ERROR"]=3
    ["CRITICAL"]=4
)

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Check if level meets threshold
    if [[ ${LOG_LEVELS[$level]} -ge ${LOG_LEVELS[$LOG_LEVEL]} ]]; then
        case "$level" in
            DEBUG)    echo -e "${CYAN}[${timestamp}] DEBUG${NC} - $message" ;;
            INFO)     echo -e "${GREEN}[${timestamp}] INFO${NC} - $message" ;;
            WARNING)  echo -e "${YELLOW}[${timestamp}] WARNING${NC} - $message" ;;
            ERROR)    echo -e "${RED}[${timestamp}] ERROR${NC} - $message" >&2 ;;
            CRITICAL) echo -e "${BOLD_RED}[${timestamp}] CRITICAL${NC} - $message" >&2 ;;
        esac

        # Also write to log file
        echo "[${timestamp}] ${level} - $message" >> "$LOG_FILE"
    fi
}

# Convenience functions
log_debug()    { log "DEBUG" "$@"; }
log_info()     { log "INFO" "$@"; }
log_warning()  { log "WARNING" "$@"; }
log_error()    { log "ERROR" "$@"; }
log_critical() { log "CRITICAL" "$@"; }
```


## 4. Display Headers


Professional header/banner display:

```bash
#!/bin/bash
# ABOUTME: Header and banner display functions
# ABOUTME: Creates consistent visual separation in CLI output

print_header() {
    local title="$1"
    local width="${2:-60}"
    local char="${3:-═}"

    local line=$(printf "%${width}s" | tr ' ' "$char")

    echo ""
    echo -e "${CYAN}${line}${NC}"
    echo -e "${CYAN}  ${title}${NC}"
    echo -e "${CYAN}${line}${NC}"
    echo ""
}

print_section() {
    local title="$1"
    echo ""
    echo -e "${BOLD}${title}${NC}"
    echo -e "${CYAN}$(printf '%.0s─' {1..40})${NC}"
}

print_status() {
    local status="$1"
    local message="$2"

    case "$status" in
        success) echo -e "  ${GREEN}✓${NC} $message" ;;
        error)   echo -e "  ${RED}✗${NC} $message" ;;
        warning) echo -e "  ${YELLOW}⚠${NC} $message" ;;
        info)    echo -e "  ${CYAN}ℹ${NC} $message" ;;
        pending) echo -e "  ${BLUE}○${NC} $message" ;;
        skip)    echo -e "  ${MAGENTA}⊘${NC} $message" ;;
    esac
}
```
