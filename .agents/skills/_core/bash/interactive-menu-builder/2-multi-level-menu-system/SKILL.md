---
name: interactive-menu-builder-2-multi-level-menu-system
description: 'Sub-skill of interactive-menu-builder: 2. Multi-Level Menu System.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 2. Multi-Level Menu System

## 2. Multi-Level Menu System


Hierarchical menu with breadcrumb navigation:

```bash
#!/bin/bash
# ABOUTME: Multi-level menu system with navigation stack
# ABOUTME: Pattern from workspace-hub workspace CLI

# Navigation stack
declare -a MENU_STACK=("main")
CURRENT_MENU="main"

# Menu definitions
declare -A MENU_TITLES=(
    ["main"]="Main Menu"
    ["repo"]="Repository Management"
    ["repo_ops"]="Repository Operations"
    ["compliance"]="Compliance & Standards"
    ["tools"]="Development Tools"
)

# Go to submenu
push_menu() {
    local menu="$1"
    MENU_STACK+=("$menu")
    CURRENT_MENU="$menu"
}

# Go back
pop_menu() {
    if [[ ${#MENU_STACK[@]} -gt 1 ]]; then
        unset 'MENU_STACK[-1]'
        CURRENT_MENU="${MENU_STACK[-1]}"
    fi
}

# Display breadcrumb
show_breadcrumb() {
    local crumb=""
    for menu in "${MENU_STACK[@]}"; do
        [[ -n "$crumb" ]] && crumb+=" > "
        crumb+="${MENU_TITLES[$menu]}"
    done
    echo -e "${CYAN}$crumb${NC}"
}

# Main menu
show_main_menu() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}              Workspace Hub - Management Console${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    show_breadcrumb
    echo ""
    echo "  1) Repository Management"
    echo "  2) Compliance & Standards"
    echo "  3) Development Tools"
    echo "  4) System Configuration"
    echo "  5) Help & Documentation"
    echo ""
    echo "  0) Exit"
    echo ""
}

# Repository submenu
show_repo_menu() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    show_breadcrumb
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  1) Repository Sync Manager"
    echo "  2) Configure Repository URLs"
    echo "  3) Check All Repository Status"
    echo "  4) Clone Repositories"
    echo ""
    echo "  0) Back"
    echo ""
}

# Handle navigation
handle_menu() {
    local choice="$1"

    case "$CURRENT_MENU" in
        main)
            case "$choice" in
                1) push_menu "repo" ;;
                2) push_menu "compliance" ;;
                3) push_menu "tools" ;;
                4) run_system_config ;;
                5) run_help ;;
                0) exit 0 ;;
            esac
            ;;
        repo)
            case "$choice" in
                1) run_repo_sync ;;
                2) run_configure_urls ;;
                3) run_check_status ;;
                4) push_menu "repo_ops" ;;
                0) pop_menu ;;
            esac
            ;;
        # Add more menus...
    esac
}

# Display current menu
show_current_menu() {
    case "$CURRENT_MENU" in
        main) show_main_menu ;;
        repo) show_repo_menu ;;
        # Add more...
    esac
}

# Main loop
while true; do
    show_current_menu
    read -p "Select option: " choice
    handle_menu "$choice"
done
```
