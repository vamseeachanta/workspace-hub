---
name: cli-productivity-1-complete-shell-configuration
description: 'Sub-skill of cli-productivity: 1. Complete Shell Configuration (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Complete Shell Configuration (+1)

## 1. Complete Shell Configuration


**~/.bashrc or ~/.zshrc:**
```bash
# ═══════════════════════════════════════════════════════════════
# CLI Productivity Configuration
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────
# Environment
# ─────────────────────────────────────────────────────────────────

export EDITOR="vim"
export VISUAL="$EDITOR"
export PAGER="bat"
export MANPAGER="sh -c 'col -bx | bat -l man -p'"

# XDG Base Directory
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

# ─────────────────────────────────────────────────────────────────
# History
# ─────────────────────────────────────────────────────────────────

HISTSIZE=50000
HISTFILESIZE=50000
HISTCONTROL=ignoreboth:erasedups
shopt -s histappend

# ─────────────────────────────────────────────────────────────────
# fzf Configuration
# ─────────────────────────────────────────────────────────────────

export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_DEFAULT_OPTS='
    --height 40%
    --layout=reverse
    --border
    --preview-window=right:50%:wrap
'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_CTRL_T_OPTS='--preview "bat --color=always --style=numbers --line-range=:500 {}"'
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
export FZF_ALT_C_OPTS='--preview "exa --tree --level=2 --color=always {}"'

# ─────────────────────────────────────────────────────────────────
# Tool Initialization
# ─────────────────────────────────────────────────────────────────

# fzf keybindings
[ -f ~/.fzf.bash ] && source ~/.fzf.bash

# zoxide
eval "$(zoxide init bash)"

# starship prompt
eval "$(starship init bash)"

# ─────────────────────────────────────────────────────────────────
# Aliases
# ─────────────────────────────────────────────────────────────────

# Modern replacements
alias ls='exa --group-directories-first'
alias ll='exa -l --group-directories-first --git'
alias la='exa -la --group-directories-first --git'
alias lt='exa --tree --level=2'
alias cat='bat --paging=never'
alias grep='rg'
alias find='fd'

# Navigation
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Git
alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline -20'
alias gd='git diff'

# Docker
alias d='docker'
alias dc='docker compose'
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# ─────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────

# Fuzzy edit
fe() {
    local file
    file=$(fzf --preview 'bat --color=always --style=numbers --line-range=:500 {}')
    [[ -n "$file" ]] && ${EDITOR:-vim} "$file"
}

# Fuzzy cd
fcd() {
    local dir
    dir=$(fd --type d | fzf --preview 'exa --tree --level=2 --color=always {}')
    [[ -n "$dir" ]] && cd "$dir"
}

# Search and edit
rge() {
    local selection
    selection=$(rg --color=always --line-number "$1" | fzf --ansi)
    if [[ -n "$selection" ]]; then
        local file=$(echo "$selection" | cut -d: -f1)
        local line=$(echo "$selection" | cut -d: -f2)
        ${EDITOR:-vim} "+$line" "$file"
    fi
}

# Create and cd
mkcd() {
    mkdir -p "$1" && cd "$1"
}
```


## 2. Data Processing Pipeline


```bash
# Process JSON API response
curl -s 'https://api.github.com/users/torvalds/repos?per_page=100' \
    | jq '.[] | {name: .name, stars: .stargazers_count}' \
    | jq -s 'sort_by(.stars) | reverse | .[0:10]'

# Find large log files and show preview
fd -e log -S +10M \
    | fzf --preview 'tail -100 {}' \
    | xargs -I{} bat --line-range=:50 {}

# Search code, preview matches, edit selected
rg --color=always -l "TODO" \
    | fzf --preview 'rg --color=always -C 3 "TODO" {}' \
    | xargs -o ${EDITOR:-vim}

# Git log with diff preview
git log --oneline --color=always \
    | fzf --ansi --preview 'git show --color=always {1}' \
    | awk '{print $1}' \
    | xargs git show
```
