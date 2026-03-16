---
name: cli-productivity-3-ripgrep-rg-fast-search
description: 'Sub-skill of cli-productivity: 3. ripgrep (rg) - Fast Search (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. ripgrep (rg) - Fast Search (+1)

## 3. ripgrep (rg) - Fast Search


**Basic Usage:**
```bash
# Search for pattern
rg "function"

# Case insensitive
rg -i "error"

# Show line numbers
rg -n "TODO"

# Search specific file types
rg --type py "import"
rg -t js "require"

# Exclude patterns
rg "pattern" --glob '!*.min.js'
rg "pattern" --glob '!node_modules'
```

**Advanced ripgrep:**
```bash
# Context lines
rg -C 3 "error"        # 3 lines before and after
rg -B 2 "error"        # 2 lines before
rg -A 2 "error"        # 2 lines after

# Fixed strings (no regex)
rg -F "func()"

# Word boundaries
rg -w "log"            # Match "log" not "logging"

# Multiple patterns
rg -e "pattern1" -e "pattern2"

# Files matching pattern
rg -l "TODO"           # List files only
rg -c "TODO"           # Count matches per file

# Inverse match
rg -v "DEBUG"          # Lines NOT containing DEBUG

# Replace
rg "old" --replace "new"

# JSON output
rg --json "pattern" | jq '.'

# Statistics
rg --stats "pattern"
```

**ripgrep Functions:**
```bash
# Search and preview with fzf
rgs() {
    rg --color=always --line-number "$1" | fzf --ansi --preview 'bat --color=always $(echo {} | cut -d: -f1) --highlight-line $(echo {} | cut -d: -f2)'
}

# Search and open in editor
rge() {
    local selection
    selection=$(rg --color=always --line-number "$1" | fzf --ansi)
    if [[ -n "$selection" ]]; then
        local file=$(echo "$selection" | cut -d: -f1)
        local line=$(echo "$selection" | cut -d: -f2)
        ${EDITOR:-vim} "+$line" "$file"
    fi
}

# Search TODOs
todos() {
    rg --color=always "TODO|FIXME|HACK|XXX" "${1:-.}" | fzf --ansi
}

# Search function definitions
funcs() {
    rg --color=always "^(def |function |async function |const .* = |class )" "${1:-.}" | fzf --ansi
}
```


## 4. fd - Fast Find


**Basic Usage:**
```bash
# Find files by name
fd "readme"

# Find with extension
fd -e md
fd -e py -e js

# Find directories
fd -t d "src"

# Find files
fd -t f "config"

# Exclude patterns
fd -E node_modules -E .git

# Hidden files
fd -H "config"

# Execute command on results
fd -e log -x rm {}
fd -e py -x wc -l {}
```

**fd Functions:**
```bash
# Find and preview
fdp() {
    fd "$@" | fzf --preview 'bat --color=always {} 2>/dev/null || exa --tree --level=2 --color=always {}'
}

# Find and edit
fde() {
    local file
    file=$(fd -t f "$@" | fzf --preview 'bat --color=always {}')
    [[ -n "$file" ]] && ${EDITOR:-vim} "$file"
}

# Find large files
fdlarge() {
    local size="${1:-100M}"
    fd -t f -S +"$size" | xargs ls -lh | sort -k5 -h
}

# Find recent files
fdrecent() {
    local days="${1:-7}"
    fd -t f --changed-within "${days}d"
}

# Find duplicates by name
fddup() {
    fd -t f | sort | uniq -d
}
```
