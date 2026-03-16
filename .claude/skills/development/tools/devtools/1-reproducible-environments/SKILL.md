---
name: devtools-1-reproducible-environments
description: 'Sub-skill of devtools: 1. Reproducible Environments (+4).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Reproducible Environments (+4)

## 1. Reproducible Environments

```bash
# Pin versions in Dockerfiles
FROM node:20.10.0-alpine

# Use lockfiles
npm ci --frozen-lockfile
pip install -r requirements.txt --require-hashes

# Document tool versions
cat > .tool-versions << 'EOF'
nodejs 20.10.0
python 3.12.0
EOF
```


## 2. Layer Optimization

```dockerfile
# Order layers by change frequency (least to most)
FROM node:20-alpine

# System dependencies (rarely change)
RUN apk add --no-cache git

# Package manifests (change sometimes)
COPY package*.json ./
RUN npm ci

# Application code (changes often)
COPY . .
```


## 3. Shell Function Library

```bash
# Create reusable functions
source_if_exists() {
    [[ -f "$1" ]] && source "$1"
}

source_if_exists "$HOME/.bashrc.local"
source_if_exists "$HOME/.bashrc.work"

# Lazy loading for slow tools
nvm() {
    unset -f nvm
    source "$NVM_DIR/nvm.sh"
    nvm "$@"
}
```


## 4. Git Configuration

```gitconfig
[alias]
    # Shortcuts
    co = checkout
    br = branch
    ci = commit
    st = status

    # Log formats
    lg = log --graph --oneline --decorate
    ll = log --pretty=format:'%C(yellow)%h%C(reset) %s %C(blue)<%an>%C(reset)'

    # Useful commands
    undo = reset --soft HEAD~1
    amend = commit --amend --no-edit
    wip = !git add -A && git commit -m 'WIP'

[core]
    autocrlf = input
    editor = vim

[pull]
    rebase = true

[push]
    autoSetupRemote = true

[rerere]
    enabled = true
```


## 5. Editor Workspace Settings

```jsonc
// .vscode/settings.json (per-project)
{
  "editor.rulers": [80, 120],
  "files.exclude": {
    "**/.git": true,
    "**/node_modules": true,
    "**/__pycache__": true
  },
  "search.exclude": {
    "**/dist": true,
    "**/coverage": true
  }
}
```
