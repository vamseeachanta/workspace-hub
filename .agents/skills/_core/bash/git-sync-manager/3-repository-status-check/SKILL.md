---
name: git-sync-manager-3-repository-status-check
description: 'Sub-skill of git-sync-manager: 3. Repository Status Check (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 3. Repository Status Check (+1)

## 3. Repository Status Check


Get detailed status for multiple repositories:

```bash
#!/bin/bash
# ABOUTME: Check git status across multiple repositories
# ABOUTME: Reports uncommitted, unpushed, and behind-remote states

check_repo_status() {
    local repo="$1"

    if [[ ! -d "$repo/.git" ]]; then
        echo "not_git"
        return
    fi

    cd "$repo" || return

    # Check for uncommitted changes
    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        echo "uncommitted"
        return
    fi

    # Check for unpushed commits
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    local ahead
    ahead=$(git rev-list --count "origin/$branch..HEAD" 2>/dev/null || echo "0")

    if [[ "$ahead" -gt 0 ]]; then
        echo "unpushed"
        return
    fi

    # Check if behind remote
    git fetch origin "$branch" --quiet 2>/dev/null
    local behind
    behind=$(git rev-list --count "HEAD..origin/$branch" 2>/dev/null || echo "0")

    if [[ "$behind" -gt 0 ]]; then
        echo "behind"
        return
    fi

    echo "clean"
}

# Batch status check
batch_status() {
    local repos=("$@")

    printf "%-30s %-15s %s\n" "Repository" "Status" "Branch"
    printf "%s\n" "────────────────────────────────────────────────────────"

    for repo in "${repos[@]}"; do
        local status
        status=$(check_repo_status "$repo")

        local branch="N/A"
        if [[ -d "$repo/.git" ]]; then
            branch=$(cd "$repo" && git rev-parse --abbrev-ref HEAD 2>/dev/null)
        fi

        local color=""
        case "$status" in
            clean)      color="${GREEN}" ;;
            uncommitted) color="${YELLOW}" ;;
            unpushed)   color="${CYAN}" ;;
            behind)     color="${RED}" ;;
            *)          color="${NC}" ;;
        esac

        printf "%-30s ${color}%-15s${NC} %s\n" "$repo" "$status" "$branch"
    done
}
```


## 4. Category-Based Operations


Filter repositories by category (Work/Personal):

```bash
#!/bin/bash
# ABOUTME: Category-based repository filtering
# ABOUTME: Parse categories from .gitignore comments

declare -A REPO_CATEGORIES

# Parse categories from .gitignore comments
# Format: repo_name/   # Category
parse_categories() {
    local gitignore="$1"

    while IFS= read -r line; do
        if [[ "$line" =~ ^([a-zA-Z0-9_-]+)/[[:space:]]*#[[:space:]]*(Personal|Work|Both)$ ]]; then
            local name="${BASH_REMATCH[1]}"
            local category="${BASH_REMATCH[2]}"
            REPO_CATEGORIES["$name"]="$category"
        fi
    done < "$gitignore"
}

# Get repos by category
get_repos_by_category() {
    local target_category="$1"
    local repos=()

    for repo in "${!REPO_CATEGORIES[@]}"; do
        local category="${REPO_CATEGORIES[$repo]}"

        if [[ "$category" == "$target_category" ]] || \
           [[ "$target_category" == "all" ]] || \
           [[ "$category" =~ $target_category ]]; then
            repos+=("$repo")
        fi
    done

    printf '%s\n' "${repos[@]}" | sort
}

# Usage
parse_categories ".gitignore"

echo "Work repositories:"
get_repos_by_category "Work"

echo "Personal repositories:"
get_repos_by_category "Personal"
```
