---
name: vscode-extensions-1-extension-management
description: 'Sub-skill of vscode-extensions: 1. Extension Management (+2).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Extension Management (+2)

## 1. Extension Management


```bash
# Keep extensions minimal
# Review periodically
code --list-extensions | wc -l

# Disable per-workspace for unused extensions
# Settings -> Extensions -> Disable (Workspace)

# Use extension packs wisely
# Create custom packs for teams
```


## 2. Performance Optimization


```jsonc
{
    // Reduce file watching
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/.git/objects/**": true,
        "**/venv/**": true
    },

    // Reduce search scope
    "search.exclude": {
        "**/node_modules": true,
        "**/dist": true
    },

    // Disable heavy features if needed
    "editor.minimap.enabled": false,
    "editor.codeLens": false,

    // Limit suggestions
    "editor.quickSuggestions": {
        "other": true,
        "comments": false,
        "strings": false
    }
}
```


## 3. Team Consistency


```jsonc
// .vscode/settings.json - Committed to repo
{
    // Consistent formatting
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode",

    // Consistent tab settings
    "editor.tabSize": 2,
    "editor.insertSpaces": true,

    // Consistent line endings
    "files.eol": "\n"
}
```
