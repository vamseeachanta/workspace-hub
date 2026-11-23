---
name: cli-productivity-3-interactive-script-template
description: 'Sub-skill of cli-productivity: 3. Interactive Script Template.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Interactive Script Template

## 3. Interactive Script Template


```bash
#!/bin/bash
# ABOUTME: Interactive CLI script using fzf and modern tools
# ABOUTME: Template for building interactive shell tools

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Check dependencies
check_deps() {
    local missing=()
    for cmd in fzf rg fd bat jq; do
        command -v "$cmd" >/dev/null || missing+=("$cmd")
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing[*]}"
        exit 1
    fi
}

# Main menu using fzf
main_menu() {
    local options=(
        "Search files"
        "Search content"
        "Edit config"
        "Run tests"
        "Exit"
    )

    local selection
    selection=$(printf '%s\n' "${options[@]}" | fzf --header="Select action:")

    case "$selection" in
        "Search files") search_files ;;
        "Search content") search_content ;;
        "Edit config") edit_config ;;
        "Run tests") run_tests ;;
        "Exit") exit 0 ;;
    esac
}

search_files() {
    local file
    file=$(fd --type f | fzf --preview 'bat --color=always {}')
    [[ -n "$file" ]] && ${EDITOR:-vim} "$file"
}

search_content() {
    local query
    read -p "Search pattern: " query
    rge "$query"
}

edit_config() {
    local configs=("~/.bashrc" "~/.vimrc" "~/.gitconfig")
    local config
    config=$(printf '%s\n' "${configs[@]}" | fzf --header="Select config:")
    [[ -n "$config" ]] && ${EDITOR:-vim} "${config/#\~/$HOME}"
}

run_tests() {
    log_info "Running tests..."
    # Add test command here
}

# Main
check_deps
while true; do
    main_menu
done
```
