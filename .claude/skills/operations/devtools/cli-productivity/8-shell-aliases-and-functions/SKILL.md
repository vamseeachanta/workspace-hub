---
name: cli-productivity-8-shell-aliases-and-functions
description: 'Sub-skill of cli-productivity: 8. Shell Aliases and Functions.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 8. Shell Aliases and Functions

## 8. Shell Aliases and Functions


**Essential Aliases:**
```bash
# Navigation
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias ~='cd ~'
alias -- -='cd -'

# Safety
alias rm='rm -i'
alias mv='mv -i'
alias cp='cp -i'

# Shortcuts
alias c='clear'
alias h='history'
alias q='exit'
alias v='vim'
alias e='${EDITOR:-vim}'

# Git shortcuts
alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline -20'
alias gd='git diff'
alias gb='git branch'
alias gco='git checkout'

# Docker shortcuts
alias d='docker'
alias dc='docker compose'
alias dps='docker ps'
alias dimg='docker images'
alias dlog='docker logs -f'

# Common directories
alias proj='cd ~/projects'
alias docs='cd ~/Documents'
alias dl='cd ~/Downloads'
```

**Utility Functions:**
```bash
# Create directory and cd into it
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Extract any archive
extract() {
    if [[ -f "$1" ]]; then
        case "$1" in
            *.tar.bz2) tar xjf "$1" ;;
            *.tar.gz)  tar xzf "$1" ;;
            *.tar.xz)  tar xJf "$1" ;;
            *.bz2)     bunzip2 "$1" ;;
            *.rar)     unrar x "$1" ;;
            *.gz)      gunzip "$1" ;;
            *.tar)     tar xf "$1" ;;
            *.tbz2)    tar xjf "$1" ;;
            *.tgz)     tar xzf "$1" ;;
            *.zip)     unzip "$1" ;;
            *.Z)       uncompress "$1" ;;
            *.7z)      7z x "$1" ;;
            *)         echo "'$1' cannot be extracted" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# Get public IP
myip() {
    curl -s https://ifconfig.me
}

# Weather
weather() {
    curl -s "wttr.in/${1:-}"
}

# Quick note
note() {
    local notes_dir="${NOTES_DIR:-$HOME/notes}"
    local date=$(date +%Y-%m-%d)
    mkdir -p "$notes_dir"
    ${EDITOR:-vim} "$notes_dir/$date.md"
}

# Serve current directory
serve() {
    local port="${1:-8000}"
    python -m http.server "$port"
}

# Show disk usage for directory
duh() {
    du -h "${1:-.}" | sort -h | tail -20
}

# Find process by name
psg() {
    ps aux | grep -v grep | grep -i "$1"
}
```
