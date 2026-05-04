---
name: git-sync-manager-1-repository-discovery-from-gitignore
description: 'Sub-skill of git-sync-manager: 1. Repository Discovery from .gitignore.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Repository Discovery from .gitignore

## 1. Repository Discovery from .gitignore


Automatically discover repositories listed in .gitignore:

```bash
#!/bin/bash
# ABOUTME: Discover repositories from .gitignore patterns
# ABOUTME: Parses directory entries and validates git repos

WORKSPACE_ROOT="${1:-.}"

# Discover repositories from .gitignore
discover_repos() {
    local repos=()

    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue

        # Extract repo name (before the /)
        local repo_name="${line%%/*}"
        [[ -z "$repo_name" ]] && continue

        # Check if directory exists and is a git repo
        if [[ -d "$WORKSPACE_ROOT/$repo_name/.git" ]]; then
            repos+=("$repo_name")
        fi
    done < <(grep -v "^[[:space:]]*#" "$WORKSPACE_ROOT/.gitignore" | grep "/" | head -100)

    printf '%s\n' "${repos[@]}"
}

# Usage
REPOS=($(discover_repos))
echo "Found ${#REPOS[@]} repositories"
```
