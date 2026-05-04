---
name: interactive-menu-builder-1-basic-menu-structure
description: 'Sub-skill of interactive-menu-builder: 1. Basic Menu Structure.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Basic Menu Structure

## 1. Basic Menu Structure


Single-level menu with numbered options:

```bash
#!/bin/bash
# ABOUTME: Basic interactive menu pattern
# ABOUTME: Simple numbered option selection

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

show_menu() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo -e "${CYAN}          Main Menu${NC}"
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo ""
    echo "  1) Option One"
    echo "  2) Option Two"
    echo "  3) Option Three"
    echo ""
    echo "  0) Exit"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo ""
}

handle_choice() {
    local choice="$1"

    case "$choice" in
        1)
            echo "Running Option One..."
            # Implementation
            ;;
        2)
            echo "Running Option Two..."
            # Implementation
            ;;
        3)
            echo "Running Option Three..."
            # Implementation
            ;;
        0)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
}

# Main loop
while true; do
    show_menu
    read -p "Select option: " choice
    handle_choice "$choice"
    echo ""
    read -p "Press Enter to continue..."
done
```
