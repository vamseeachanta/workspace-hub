---
name: obsidian-integration-with-git-repositories
description: 'Sub-skill of obsidian: Integration with Git Repositories.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Integration with Git Repositories

## Integration with Git Repositories


```bash
#!/bin/bash
# Link project documentation to code repository

PROJECT_NAME="my-project"
CODE_REPO="$HOME/code/$PROJECT_NAME"
VAULT_PATH="$HOME/Documents/ObsidianVault"

# Create project folder in vault
mkdir -p "$VAULT_PATH/Projects/$PROJECT_NAME"

# Symlink docs folder from code repo
ln -s "$CODE_REPO/docs" "$VAULT_PATH/Projects/$PROJECT_NAME/Docs"

# Create project overview note
cat > "$VAULT_PATH/Projects/$PROJECT_NAME/Overview.md" << EOF
---
title: $PROJECT_NAME
type: project
repo: $CODE_REPO
status: active
---

# $PROJECT_NAME
