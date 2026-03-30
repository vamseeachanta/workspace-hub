---
name: vscode-extensions-4-keybindings-configuration
description: 'Sub-skill of vscode-extensions: 4. Keybindings Configuration.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 4. Keybindings Configuration

## 4. Keybindings Configuration


```jsonc
// keybindings.json
// Location: ~/.config/Code/User/keybindings.json (Linux)
[
    // Navigation
    {
        "key": "ctrl+shift+e",
        "command": "workbench.view.explorer"
    },
    {
        "key": "ctrl+shift+g",
        "command": "workbench.view.scm"
    },
    {
        "key": "ctrl+shift+f",
        "command": "workbench.view.search"
    },
    {
        "key": "ctrl+shift+d",
        "command": "workbench.view.debug"
    },
    {
        "key": "ctrl+shift+x",
        "command": "workbench.view.extensions"
    },

    // Terminal
    {
        "key": "ctrl+`",
        "command": "workbench.action.terminal.toggleTerminal"
    },
    {
        "key": "ctrl+shift+`",
        "command": "workbench.action.terminal.new"
    },
    {
        "key": "ctrl+shift+c",
        "command": "workbench.action.terminal.openNativeConsole"
    },

    // Editor navigation
    {
        "key": "ctrl+tab",
        "command": "workbench.action.nextEditor"
    },
    {
        "key": "ctrl+shift+tab",
        "command": "workbench.action.previousEditor"
    },
    {
        "key": "alt+left",
        "command": "workbench.action.navigateBack"
    },
    {
        "key": "alt+right",
        "command": "workbench.action.navigateForward"
    },

    // Line manipulation
    {
        "key": "alt+up",
        "command": "editor.action.moveLinesUpAction",
        "when": "editorTextFocus && !editorReadonly"
    },
    {
        "key": "alt+down",
        "command": "editor.action.moveLinesDownAction",
        "when": "editorTextFocus && !editorReadonly"
    },
    {
        "key": "shift+alt+up",
        "command": "editor.action.copyLinesUpAction",
        "when": "editorTextFocus && !editorReadonly"
    },
    {
        "key": "shift+alt+down",
        "command": "editor.action.copyLinesDownAction",
        "when": "editorTextFocus && !editorReadonly"
    },
    {
        "key": "ctrl+shift+k",
        "command": "editor.action.deleteLines",
        "when": "editorTextFocus && !editorReadonly"
    },

    // Selection
    {
        "key": "ctrl+l",
        "command": "expandLineSelection",
        "when": "editorTextFocus"
    },
    {
        "key": "ctrl+d",
        "command": "editor.action.addSelectionToNextFindMatch",
        "when": "editorFocus"
    },
    {
        "key": "ctrl+shift+l",
        "command": "editor.action.selectHighlights",
        "when": "editorFocus"
    },

    // Multi-cursor
    {
        "key": "ctrl+alt+up",
        "command": "editor.action.insertCursorAbove",
        "when": "editorTextFocus"
    },
    {
        "key": "ctrl+alt+down",
        "command": "editor.action.insertCursorBelow",
        "when": "editorTextFocus"
    },

    // Code actions
    {
        "key": "ctrl+.",
        "command": "editor.action.quickFix",
        "when": "editorHasCodeActionsProvider && editorTextFocus && !editorReadonly"
    },
    {
        "key": "f2",
        "command": "editor.action.rename",
        "when": "editorHasRenameProvider && editorTextFocus && !editorReadonly"
    },
    {
        "key": "f12",
        "command": "editor.action.revealDefinition",
        "when": "editorHasDefinitionProvider && editorTextFocus"
    },
    {
        "key": "alt+f12",
        "command": "editor.action.peekDefinition",
        "when": "editorHasDefinitionProvider && editorTextFocus"
    },
    {
        "key": "shift+f12",
        "command": "editor.action.goToReferences",
        "when": "editorHasReferenceProvider && editorTextFocus"
    },

    // Formatting
    {
        "key": "shift+alt+f",
        "command": "editor.action.formatDocument",
        "when": "editorTextFocus && !editorReadonly"
    },
    {
        "key": "ctrl+k ctrl+f",
        "command": "editor.action.formatSelection",
        "when": "editorHasDocumentSelectionFormattingProvider && editorTextFocus && !editorReadonly"
    },

    // Comments
    {
        "key": "ctrl+/",
        "command": "editor.action.commentLine",
        "when": "editorTextFocus && !editorReadonly"
    },
    {
        "key": "shift+alt+a",
        "command": "editor.action.blockComment",
        "when": "editorTextFocus && !editorReadonly"
    },

    // Fold/unfold
    {
        "key": "ctrl+shift+[",
        "command": "editor.fold",
        "when": "editorTextFocus"
    },
    {
        "key": "ctrl+shift+]",
        "command": "editor.unfold",
        "when": "editorTextFocus"
    },
    {
        "key": "ctrl+k ctrl+0",
        "command": "editor.foldAll"
    },
    {
        "key": "ctrl+k ctrl+j",
        "command": "editor.unfoldAll"
    },

*Content truncated — see parent skill for full reference.*
