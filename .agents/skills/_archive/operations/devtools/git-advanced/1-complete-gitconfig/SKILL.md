---
name: git-advanced-1-complete-gitconfig
description: 'Sub-skill of git-advanced: 1. Complete .gitconfig (+2).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Complete .gitconfig (+2)

## 1. Complete .gitconfig


```gitconfig
# ~/.gitconfig

[user]
    name = Your Name
    email = your.email@example.com

[core]
    editor = vim
    autocrlf = input
    pager = delta

[init]
    defaultBranch = main

[pull]
    rebase = true

[push]
    autoSetupRemote = true
    default = current

[fetch]
    prune = true
    pruneTags = true

[merge]
    conflictStyle = diff3
    ff = false

[rebase]
    autosquash = true
    autostash = true

[rerere]
    enabled = true

[diff]
    algorithm = histogram
    colorMoved = default

[status]
    showUntrackedFiles = all

[credential]
    helper = cache --timeout=3600

[alias]
    # Core aliases
    st = status -sb
    co = checkout
    br = branch
    ci = commit
    lg = log --graph --oneline --decorate -20

    # Workflow aliases
    undo = reset --soft HEAD~1
    wip = !git add -A && git commit -m 'WIP'
    sync = !git fetch --all --prune && git pull --rebase

    # Branch cleanup
    cleanup = !git branch --merged main | grep -v '^[ *]*main$' | xargs git branch -d

[delta]
    navigate = true
    side-by-side = true
    line-numbers = true

[interactive]
    diffFilter = delta --color-only
```


## 2. GitHub Workflow with Hooks


```yaml
# .github/workflows/pr-check.yml
name: PR Checks

on:
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Validate commit messages
        run: |
          COMMITS=$(git log --format="%s" origin/main..HEAD)
          PATTERN="^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"
          while IFS= read -r commit; do
            if ! echo "$commit" | grep -qE "$PATTERN"; then
              echo "Invalid commit message: $commit"
              exit 1
            fi
          done <<< "$COMMITS"

      - name: Check for merge commits
        run: |
          MERGE_COMMITS=$(git log --merges origin/main..HEAD --oneline)
          if [ -n "$MERGE_COMMITS" ]; then
            echo "Merge commits found. Please rebase instead."
            echo "$MERGE_COMMITS"
            exit 1
          fi

      - name: Run tests
        run: npm test
```


## 3. Git Flow Helper Functions


```bash
# Add to ~/.bashrc

# Start feature
gf-start() {
    local feature="$1"
    git checkout main
    git pull
    git checkout -b "feature/$feature"
}

# Finish feature
gf-finish() {
    local branch=$(git rev-parse --abbrev-ref HEAD)
    git checkout main
    git pull
    git merge --no-ff "$branch"
    git branch -d "$branch"
}

# Start hotfix
gh-start() {
    local hotfix="$1"
    git checkout main
    git pull
    git checkout -b "hotfix/$hotfix"
}

# Sync branch with main
gsync() {
    local branch=$(git rev-parse --abbrev-ref HEAD)
    git fetch origin main:main
    git rebase main
}
```
