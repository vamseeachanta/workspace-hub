---
name: vscode-extensions-6-workspace-configuration
description: 'Sub-skill of vscode-extensions: 6. Workspace Configuration.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 6. Workspace Configuration

## 6. Workspace Configuration


```jsonc
// .vscode/settings.json - Project-specific settings
{
    // Project-specific formatters
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true,

    // Python project
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest",
    "python.testing.pytestArgs": ["tests"],
    "python.analysis.extraPaths": ["${workspaceFolder}/src"],

    // File associations
    "files.associations": {
        "*.env.*": "dotenv",
        "Dockerfile.*": "dockerfile"
    },

    // Search exclusions
    "search.exclude": {
        "**/node_modules": true,
        "**/.venv": true,
        "**/dist": true,
        "**/coverage": true
    },

    // Ruler for this project
    "editor.rulers": [88, 120],

    // Custom dictionary words
    "cSpell.words": [
        "pytest",
        "asyncio",
        "pydantic"
    ]
}
```

```jsonc
// .vscode/extensions.json - Recommended extensions
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint",
        "eamodio.gitlens",
        "usernamehw.errorlens"
    ],
    "unwantedRecommendations": []
}
```

```jsonc
// .vscode/tasks.json - Build and run tasks
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "pytest",
            "args": ["tests/", "-v", "--cov=src"],
            "group": {
                "kind": "test",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Lint",
            "type": "shell",
            "command": "ruff",
            "args": ["check", "src/"],
            "group": "build",
            "presentation": {
                "reveal": "silent",
                "panel": "shared"
            },
            "problemMatcher": {
                "owner": "ruff",
                "fileLocation": ["relative", "${workspaceFolder}"],
                "pattern": {
                    "regexp": "^(.+):(\\d+):(\\d+): (\\w+) (.+)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "label": "Format",
            "type": "shell",
            "command": "black",
            "args": ["src/", "tests/"],
            "group": "build",
            "presentation": {
                "reveal": "silent"
            }
        },
        {
            "label": "Build Docker",
            "type": "shell",
            "command": "docker",
            "args": ["build", "-t", "${workspaceFolderBasename}:latest", "."],
            "group": "build",
            "presentation": {
                "reveal": "always"
            }
        },
        {
            "label": "Start Dev Server",
            "type": "shell",
            "command": "python",
            "args": ["-m", "uvicorn", "src.main:app", "--reload"],
            "isBackground": true,
            "problemMatcher": {
                "pattern": {
                    "regexp": "."
                },
                "background": {
                    "activeOnStart": true,
                    "beginsPattern": "^.*Uvicorn running.*$",
                    "endsPattern": "^.*Application startup complete.*$"
                }
            }
        }
    ]
}
```

```jsonc
// .vscode/launch.json - Debug configurations
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": ["src.main:app", "--reload", "--port", "8000"],
            "jinja": true,
            "justMyCode": true,
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Python: pytest",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v", "-s"],
            "console": "integratedTerminal"
        },
        {
            "name": "Node: Current File",
            "type": "node",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Node: npm start",
            "type": "node",
            "request": "launch",

*Content truncated — see parent skill for full reference.*
