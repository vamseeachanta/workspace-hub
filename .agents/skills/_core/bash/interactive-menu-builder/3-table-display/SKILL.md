---
name: interactive-menu-builder-3-table-display
description: 'Sub-skill of interactive-menu-builder: 3. Table Display (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 3. Table Display (+1)

## 3. Table Display


Display data in formatted tables:

```bash
#!/bin/bash
# ABOUTME: Table display functions for CLI menus
# ABOUTME: Format data in aligned columns with headers

# Print table header
print_table_header() {
    local -a headers=("$@")
    local format=""

    # Build format string
    for header in "${headers[@]}"; do
        format+="%-20s "
    done

    echo ""
    printf "${CYAN}${format}${NC}\n" "${headers[@]}"
    printf "${CYAN}%s${NC}\n" "$(printf '─%.0s' {1..80})"
}

# Print table row
print_table_row() {
    local format=""
    local -a values=("$@")

    for _ in "${values[@]}"; do
        format+="%-20s "
    done

    printf "${format}\n" "${values[@]}"
}

# Display repository table
show_repo_table() {
    print_table_header "Repository" "Category" "Status" "Branch"

    for repo in "${REPOS[@]}"; do
        local category=$(get_category "$repo")
        local status=$(get_status "$repo")
        local branch=$(get_branch "$repo")

        # Color-code status
        case "$status" in
            "Clean")      status="${GREEN}Clean${NC}" ;;
            "Modified")   status="${YELLOW}Modified${NC}" ;;
            "Untracked")  status="${RED}Untracked${NC}" ;;
        esac

        print_table_row "$repo" "$category" "$status" "$branch"
    done
}
```


## 4. Selection Lists


Let users select from a list:

```bash
#!/bin/bash
# ABOUTME: Selection list patterns
# ABOUTME: Single and multi-select from numbered lists

# Single selection
select_single() {
    local prompt="$1"
    shift
    local -a options=("$@")

    echo ""
    for i in "${!options[@]}"; do
        echo "  $((i+1))) ${options[$i]}"
    done
    echo ""
    echo "  0) Cancel"
    echo ""

    read -p "$prompt: " choice

    if [[ "$choice" == "0" ]]; then
        return 1
    elif [[ "$choice" -ge 1 && "$choice" -le ${#options[@]} ]]; then
        SELECTED="${options[$((choice-1))]}"
        return 0
    else
        echo -e "${RED}Invalid selection${NC}"
        return 1
    fi
}

# Multi-selection
select_multiple() {
    local prompt="$1"
    shift
    local -a options=("$@")
    local -a selected=()

    echo ""
    echo "Enter numbers separated by spaces (or 'all' for all):"
    echo ""

    for i in "${!options[@]}"; do
        echo "  $((i+1))) ${options[$i]}"
    done
    echo ""

    read -p "$prompt: " input

    if [[ "$input" == "all" ]]; then
        SELECTED=("${options[@]}")
        return 0
    fi

    for num in $input; do
        if [[ "$num" -ge 1 && "$num" -le ${#options[@]} ]]; then
            selected+=("${options[$((num-1))]}")
        fi
    done

    SELECTED=("${selected[@]}")
    [[ ${#SELECTED[@]} -gt 0 ]]
}

# Usage
repos=("repo1" "repo2" "repo3" "repo4")

if select_single "Select repository" "${repos[@]}"; then
    echo "You selected: $SELECTED"
fi

if select_multiple "Select repositories" "${repos[@]}"; then
    echo "You selected: ${SELECTED[*]}"
fi
```
