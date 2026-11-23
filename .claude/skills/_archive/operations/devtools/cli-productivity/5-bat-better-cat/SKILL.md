---
name: cli-productivity-5-bat-better-cat
description: 'Sub-skill of cli-productivity: 5. bat - Better cat (+2).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 5. bat - Better cat (+2)

## 5. bat - Better cat


**Basic Usage:**
```bash
# Syntax highlighted output
bat file.py

# Show line numbers
bat -n file.py

# Show all non-printable chars
bat -A file.py

# Multiple files
bat file1.py file2.py

# Plain output (no decorations)
bat -p file.py

# Specific language
bat -l json data.txt

# Diff two files
bat --diff file1 file2
```

**bat Configuration:**
```bash
# Add to ~/.bashrc or ~/.zshrc

# Set bat as default pager
export MANPAGER="sh -c 'col -bx | bat -l man -p'"
export PAGER="bat"

# Bat theme
export BAT_THEME="TwoDark"

# Bat style
export BAT_STYLE="numbers,changes,header"
```

**bat Aliases:**
```bash
# Replace cat with bat
alias cat='bat --paging=never'

# Preview alias for fzf
alias preview='fzf --preview "bat --color=always {}"'

# Pretty print JSON
alias json='bat -l json'

# Pretty print YAML
alias yaml='bat -l yaml'

# Diff with bat
alias diff='bat --diff'
```


## 6. exa/eza - Better ls


**Basic Usage:**
```bash
# Basic list
exa

# Long format
exa -l

# All files including hidden
exa -la

# Tree view
exa --tree
exa --tree --level=2

# Sort by modified
exa -l --sort=modified

# With git status
exa -l --git

# Group directories first
exa -l --group-directories-first

# Icons
exa -l --icons
```

**exa Aliases:**
```bash
# Add to ~/.bashrc or ~/.zshrc

# Replace ls with exa
alias ls='exa --group-directories-first'
alias ll='exa -l --group-directories-first --git'
alias la='exa -la --group-directories-first --git'
alias lt='exa --tree --level=2'
alias lta='exa --tree --level=2 -a'

# With icons (if supported)
alias li='exa -l --icons --group-directories-first --git'
```


## 7. zoxide - Smart cd


**Basic Usage:**
```bash
# Initialize (add to shell rc)
eval "$(zoxide init bash)"  # or zsh

# Use z instead of cd
z projects          # Jump to most frequent/recent match
z pro               # Partial match

# Interactive selection
zi                  # Opens fzf for selection

# Add directory manually
zoxide add /path/to/dir

# Query database
zoxide query projects
zoxide query -l     # List all entries
```

**zoxide Configuration:**
```bash
# Add to ~/.bashrc or ~/.zshrc

# Initialize zoxide
eval "$(zoxide init bash --cmd cd)"  # Replace cd

# Or use custom command
eval "$(zoxide init bash --cmd j)"   # Use 'j' for jump
```
