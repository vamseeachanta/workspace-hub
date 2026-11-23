---
name: git-advanced-7-git-aliases
description: 'Sub-skill of git-advanced: 7. Git Aliases (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 7. Git Aliases (+1)

## 7. Git Aliases


**Useful Aliases:**
```bash
# Add to ~/.gitconfig
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
```

**Advanced Aliases:**
```gitconfig
# ~/.gitconfig
[alias]
    # Status
    st = status -sb
    ss = status

    # Branch operations
    br = branch
    bra = branch -a
    brd = branch -d
    brD = branch -D

    # Checkout
    co = checkout
    cob = checkout -b
    com = checkout main

    # Commit
    ci = commit
    cia = commit --amend
    ciane = commit --amend --no-edit
    wip = !git add -A && git commit -m 'WIP'

    # Diff
    df = diff
    dfs = diff --staged
    dfw = diff --word-diff

    # Log
    lg = log --graph --oneline --decorate -20
    lga = log --graph --oneline --decorate --all
    ll = log --pretty=format:'%C(yellow)%h%C(reset) %s %C(blue)<%an>%C(reset) %C(green)(%cr)%C(reset)' -20
    hist = log --pretty=format:'%h %ad | %s%d [%an]' --graph --date=short

    # Stash
    sl = stash list
    sp = stash pop
    ss = stash save
    sd = stash drop

    # Remote
    pu = push
    puf = push --force-with-lease
    pl = pull
    plr = pull --rebase
    fe = fetch --all --prune

    # Rebase
    rb = rebase
    rbi = rebase -i
    rbc = rebase --continue
    rba = rebase --abort

    # Reset
    undo = reset --soft HEAD~1
    nuke = reset --hard HEAD

    # Clean
    clean-branches = !git branch --merged | grep -v '*' | xargs -n 1 git branch -d

    # Find
    find = !git ls-files | grep -i
    grep = grep -Ii

    # Utility
    aliases = !git config --get-regexp '^alias\\.' | sed 's/alias\\.\\([^ ]*\\) \\(.*\\)/\\1\\\t => \\2/' | sort
    contributors = shortlog -sn
```


## 8. Submodules


**Basic Submodule Operations:**
```bash
# Add submodule
git submodule add https://github.com/user/repo libs/repo

# Clone with submodules
git clone --recurse-submodules https://github.com/user/main-repo

# Initialize submodules after clone
git submodule init
git submodule update

# Or combined
git submodule update --init --recursive

# Update submodule to latest
cd libs/repo
git checkout main
git pull
cd ../..
git add libs/repo
git commit -m "Update submodule"

# Update all submodules
git submodule update --remote
```

**Submodule Configuration:**
```bash
# Track specific branch
git config -f .gitmodules submodule.libs/repo.branch main

# Shallow clone submodules
git config -f .gitmodules submodule.libs/repo.shallow true

# Update strategy
git submodule update --remote --merge  # Merge changes
git submodule update --remote --rebase # Rebase changes
```

**Submodule Workflow Script:**
```bash
#!/bin/bash
# scripts/submodule-sync.sh
# ABOUTME: Synchronize all submodules
# ABOUTME: Updates submodules to latest remote commits

set -e

echo "Synchronizing submodules..."

# Initialize any new submodules
git submodule init

# Update all submodules to tracked branch
git submodule update --remote --merge

# Show status
git submodule status

echo "Submodules synchronized!"
```
