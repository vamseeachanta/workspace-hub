---
name: interactive-menu-builder-5-confirmation-dialogs
description: 'Sub-skill of interactive-menu-builder: 5. Confirmation Dialogs (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 5. Confirmation Dialogs (+1)

## 5. Confirmation Dialogs


Request user confirmation:

```bash
#!/bin/bash
# ABOUTME: Confirmation dialog patterns
# ABOUTME: Yes/No prompts with defaults

# Simple yes/no
confirm() {
    local prompt="${1:-Are you sure?}"
    local default="${2:-n}"  # Default to no

    if [[ "$default" == "y" ]]; then
        prompt+=" [Y/n]: "
    else
        prompt+=" [y/N]: "
    fi

    read -p "$prompt" response
    response="${response:-$default}"

    [[ "${response,,}" == "y" || "${response,,}" == "yes" ]]
}

# Confirmation with explanation
confirm_action() {
    local action="$1"
    local details="$2"

    echo ""
    echo -e "${YELLOW}⚠ Confirmation Required${NC}"
    echo ""
    echo "Action: $action"
    [[ -n "$details" ]] && echo "Details: $details"
    echo ""

    confirm "Proceed?" "n"
}

# Dangerous action confirmation
confirm_dangerous() {
    local action="$1"
    local confirm_word="${2:-DELETE}"

    echo ""
    echo -e "${RED}⚠ DANGEROUS OPERATION${NC}"
    echo ""
    echo "This action cannot be undone!"
    echo "Action: $action"
    echo ""
    echo -e "Type '${YELLOW}${confirm_word}${NC}' to confirm:"

    read -p "> " response
    [[ "$response" == "$confirm_word" ]]
}

# Usage
if confirm "Delete all logs?"; then
    rm -rf logs/*
fi

if confirm_dangerous "Delete all repositories" "DELETE"; then
    # Perform dangerous action
    echo "Proceeding..."
fi
```


## 6. Progress Indicators


Show progress during operations:

```bash
#!/bin/bash
# ABOUTME: Progress indicator patterns
# ABOUTME: Spinners, bars, and status updates

# Spinner
spinner() {
    local pid=$1
    local message="${2:-Processing}"
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0

    while kill -0 "$pid" 2>/dev/null; do
        i=$(( (i+1) % ${#spin} ))
        printf "\r${CYAN}%s${NC} %s" "${spin:$i:1}" "$message"
        sleep 0.1
    done

    printf "\r${GREEN}✓${NC} %s\n" "$message"
}

# Usage
long_running_task &
spinner $! "Running long task..."

# Progress bar
progress_bar() {
    local current=$1
    local total=$2
    local width=40
    local percent=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))

    printf "\r["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %3d%% (%d/%d)" "$percent" "$current" "$total"
}

# Usage
total=100
for i in $(seq 1 $total); do
    progress_bar $i $total
    sleep 0.05
done
echo ""

# Status updates
status_line() {
    local message="$1"
    printf "\r\033[K%s" "$message"  # Clear line and print
}

# Completion markers
mark_done() {
    local message="$1"
    echo -e "${GREEN}✓${NC} $message"
}

mark_fail() {
    local message="$1"
    echo -e "${RED}✗${NC} $message"
}

mark_skip() {
    local message="$1"
    echo -e "${YELLOW}⊘${NC} $message"
}
```
