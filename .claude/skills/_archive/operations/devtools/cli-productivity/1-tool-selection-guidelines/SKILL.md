---
name: cli-productivity-1-tool-selection-guidelines
description: 'Sub-skill of cli-productivity: 1. Tool Selection Guidelines (+2).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Tool Selection Guidelines (+2)

## 1. Tool Selection Guidelines


| Task | Tool | Why |
|------|------|-----|
| Find files by name | fd | Fast, intuitive syntax |
| Find files by content | rg | Faster than grep, better defaults |
| View files | bat | Syntax highlighting, line numbers |
| List files | exa | Icons, git status, tree view |
| Navigate directories | zoxide | Learns your patterns |
| Interactive selection | fzf | Fuzzy matching, preview |
| Process JSON | jq | Powerful, composable |


## 2. Performance Tips


```bash
# Use fd instead of find
fd "pattern"              # Instead of: find . -name "*pattern*"

# Use rg instead of grep
rg "pattern"              # Instead of: grep -r "pattern" .

# Limit search depth
fd --max-depth 3
rg --max-depth 3

# Exclude directories
fd -E node_modules -E .git
rg --glob '!node_modules'
```


## 3. Shell Startup Optimization


```bash
# Lazy load slow tools
nvm() {
    unset -f nvm
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    nvm "$@"
}

# Cache expensive operations
_update_ps1_cache() {
    PS1_CACHE="$(expensive_command)"
}
```
