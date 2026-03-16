---
name: devtools-integration-with-workspace-hub
description: 'Sub-skill of devtools: Integration with Workspace-Hub.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Integration with Workspace-Hub

## Integration with Workspace-Hub


These skills power development workflows:

```
workspace-hub/
├── docker/
│   ├── Dockerfile           # Uses: docker
│   └── docker-compose.yml   # Uses: docker
├── .vscode/
│   ├── settings.json        # Uses: vscode-extensions
│   ├── extensions.json
│   └── tasks.json
├── scripts/
│   ├── dev-setup.sh         # Uses: cli-productivity
│   └── git-helpers.sh       # Uses: git-advanced
├── .githooks/
│   ├── pre-commit           # Uses: git-advanced
│   └── commit-msg
└── dotfiles/
    ├── .bashrc              # Uses: cli-productivity
    └── .gitconfig           # Uses: git-advanced
```
