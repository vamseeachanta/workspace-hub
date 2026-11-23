---
name: vscode-extensions-git-workflow-integration
description: 'Sub-skill of vscode-extensions: Git Workflow Integration (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Git Workflow Integration (+1)

## Git Workflow Integration


```jsonc
// settings.json - Git integration
{
    "git.autofetch": true,
    "git.confirmSync": false,
    "git.enableSmartCommit": true,
    "git.postCommitCommand": "push",
    "git.fetchOnPull": true,
    "git.pruneOnFetch": true,

    // GitLens settings
    "gitlens.views.repositories.branches.layout": "tree",
    "gitlens.views.commits.files.layout": "tree",
    "gitlens.codeLens.enabled": true,
    "gitlens.codeLens.recentChange.enabled": true,
    "gitlens.currentLine.enabled": true,
    "gitlens.hovers.currentLine.over": "line",
    "gitlens.blame.format": "${author|10} ${date}",
    "gitlens.blame.heatmap.enabled": true
}
```


## Remote Development


```jsonc
// settings.json - Remote development
{
    // SSH
    "remote.SSH.remotePlatform": {
        "server1": "linux",
        "server2": "linux"
    },
    "remote.SSH.defaultExtensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
    ],

    // Containers
    "dev.containers.defaultExtensions": [
        "ms-python.python",
        "eamodio.gitlens"
    ],

    // WSL
    "remote.WSL.fileWatcher.polling": true
}
```

```jsonc
// .devcontainer/devcontainer.json
{
    "name": "Python Dev",
    "image": "mcr.microsoft.com/devcontainers/python:3.12",
    "features": {
        "ghcr.io/devcontainers/features/docker-in-docker:2": {}
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "charliermarsh.ruff"
            ],
            "settings": {
                "python.defaultInterpreterPath": "/usr/local/bin/python"
            }
        }
    },
    "postCreateCommand": "pip install -e '.[dev]'",
    "forwardPorts": [8000]
}
```
