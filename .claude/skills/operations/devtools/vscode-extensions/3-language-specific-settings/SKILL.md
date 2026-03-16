---
name: vscode-extensions-3-language-specific-settings
description: 'Sub-skill of vscode-extensions: 3. Language-Specific Settings.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Language-Specific Settings

## 3. Language-Specific Settings


```jsonc
// settings.json - Language-specific overrides
{
    // Python
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "editor.tabSize": 4,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit"
        }
    },
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "python.terminal.activateEnvironment": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "ruff.organizeImports": true,

    // JavaScript/TypeScript
    "[javascript]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[typescript]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[typescriptreact]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[javascriptreact]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "typescript.preferences.importModuleSpecifier": "relative",
    "typescript.updateImportsOnFileMove.enabled": "always",

    // JSON
    "[json]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[jsonc]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },

    // YAML
    "[yaml]": {
        "editor.defaultFormatter": "redhat.vscode-yaml",
        "editor.tabSize": 2,
        "editor.autoIndent": "advanced"
    },
    "yaml.schemas": {
        "https://json.schemastore.org/github-workflow.json": ".github/workflows/*.yml"
    },

    // Markdown
    "[markdown]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.wordWrap": "on",
        "editor.quickSuggestions": {
            "other": true,
            "comments": false,
            "strings": true
        }
    },
    "markdown.preview.fontSize": 14,

    // HTML/CSS
    "[html]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[css]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[scss]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },

    // Go
    "[go]": {
        "editor.defaultFormatter": "golang.go",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "always"
        }
    },
    "go.lintTool": "golangci-lint",
    "go.testOnSave": true,

    // Rust
    "[rust]": {
        "editor.defaultFormatter": "rust-lang.rust-analyzer",
        "editor.formatOnSave": true
    },
    "rust-analyzer.checkOnSave.command": "clippy",

    // Shell
    "[shellscript]": {
        "editor.defaultFormatter": "foxundermoon.shell-format",
        "editor.tabSize": 4
    }
}
```
