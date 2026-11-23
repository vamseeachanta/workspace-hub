---
name: devtools-environment-configuration
description: 'Sub-skill of devtools: Environment Configuration (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Environment Configuration (+3)

## Environment Configuration


```bash
# XDG Base Directory
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

# Tool-specific
export DOCKER_CONFIG="$XDG_CONFIG_HOME/docker"
export HISTFILE="$XDG_DATA_HOME/bash/history"
```

## Dotfile Management


```bash
# Symlink configuration
link_dotfiles() {
    local dotfiles_dir="$HOME/dotfiles"

    ln -sf "$dotfiles_dir/.bashrc" "$HOME/.bashrc"
    ln -sf "$dotfiles_dir/.gitconfig" "$HOME/.gitconfig"
    ln -sf "$dotfiles_dir/config/nvim" "$XDG_CONFIG_HOME/nvim"
}
```

## Tool Version Management


```bash
# Version switching pattern
use_tool_version() {
    local tool="$1"
    local version="$2"

    case "$tool" in
        node) nvm use "$version" ;;
        python) pyenv shell "$version" ;;
        ruby) rbenv shell "$version" ;;
        go) goenv shell "$version" ;;
    esac
}
```

## Path Management


```bash
# Add to PATH safely
add_to_path() {
    local dir="$1"
    [[ ":$PATH:" != *":$dir:"* ]] && export PATH="$dir:$PATH"
}

add_to_path "$HOME/.local/bin"
add_to_path "$HOME/go/bin"
```
