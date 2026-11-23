---
name: vscode-extensions-2-settings-configuration
description: 'Sub-skill of vscode-extensions: 2. Settings Configuration.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 2. Settings Configuration

## 2. Settings Configuration


```jsonc
// settings.json - User settings
// Location: ~/.config/Code/User/settings.json (Linux)
//           ~/Library/Application Support/Code/User/settings.json (macOS)
//           %APPDATA%\Code\User\settings.json (Windows)
{
    // Editor appearance
    "editor.fontSize": 14,
    "editor.fontFamily": "'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace",
    "editor.fontLigatures": true,
    "editor.lineHeight": 1.6,
    "editor.letterSpacing": 0.5,
    "editor.cursorBlinking": "smooth",
    "editor.cursorSmoothCaretAnimation": "on",
    "editor.smoothScrolling": true,

    // Editor behavior
    "editor.lineNumbers": "relative",
    "editor.rulers": [80, 120],
    "editor.wordWrap": "off",
    "editor.minimap.enabled": false,
    "editor.renderWhitespace": "boundary",
    "editor.bracketPairColorization.enabled": true,
    "editor.guides.bracketPairs": "active",
    "editor.stickyScroll.enabled": true,
    "editor.inlineSuggest.enabled": true,

    // Code formatting
    "editor.formatOnSave": true,
    "editor.formatOnPaste": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit"
    },

    // Tab and indentation
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.detectIndentation": true,
    "editor.trimAutoWhitespace": true,

    // Search and navigation
    "editor.quickSuggestions": {
        "other": true,
        "comments": false,
        "strings": true
    },
    "editor.suggestSelection": "first",
    "editor.acceptSuggestionOnEnter": "on",
    "editor.snippetSuggestions": "top",

    // Files
    "files.autoSave": "onFocusChange",
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "files.trimFinalNewlines": true,
    "files.exclude": {
        "**/.git": true,
        "**/.DS_Store": true,
        "**/node_modules": true,
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/venv": true,
        "**/.venv": true
    },
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/.git/objects/**": true
    },

    // Search
    "search.exclude": {
        "**/node_modules": true,
        "**/dist": true,
        "**/build": true,
        "**/coverage": true,
        "**/.next": true
    },
    "search.useIgnoreFiles": true,
    "search.smartCase": true,

    // Terminal
    "terminal.integrated.fontSize": 13,
    "terminal.integrated.fontFamily": "'JetBrains Mono', 'MesloLGS NF', monospace",
    "terminal.integrated.cursorStyle": "line",
    "terminal.integrated.defaultProfile.osx": "zsh",
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.scrollback": 10000,

    // Git
    "git.autofetch": true,
    "git.confirmSync": false,
    "git.enableSmartCommit": true,
    "git.openRepositoryInParentFolders": "always",
    "gitlens.currentLine.enabled": true,
    "gitlens.hovers.currentLine.over": "line",

    // Workbench
    "workbench.startupEditor": "none",
    "workbench.editor.enablePreview": false,
    "workbench.editor.tabCloseButton": "right",
    "workbench.colorTheme": "GitHub Dark Default",
    "workbench.iconTheme": "material-icon-theme",
    "workbench.tree.indent": 20,
    "workbench.tree.renderIndentGuides": "always",

    // Breadcrumbs
    "breadcrumbs.enabled": true,
    "breadcrumbs.filePath": "on",

    // Explorer
    "explorer.confirmDelete": false,
    "explorer.confirmDragAndDrop": false,
    "explorer.compactFolders": false,
    "explorer.sortOrder": "type",

    // Zen Mode
    "zenMode.hideLineNumbers": false,
    "zenMode.centerLayout": true,

    // Extensions
    "errorLens.enabled": true,
    "errorLens.enabledDiagnosticLevels": ["error", "warning"],
    "todo-tree.general.tags": ["TODO", "FIXME", "BUG", "HACK", "XXX", "NOTE"],

    // Telemetry
    "telemetry.telemetryLevel": "off"
}
```
