---
name: automation-integration-with-workspace-hub
description: 'Sub-skill of automation: Integration with Workspace-Hub.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Integration with Workspace-Hub

## Integration with Workspace-Hub


These skills power automation across the workspace-hub ecosystem:

```
workspace-hub/
├── .github/
│   └── workflows/           # Uses: github-actions
│       ├── ci.yml
│       ├── release.yml
│       └── sync.yml
├── automation/
│   ├── n8n/                 # Uses: n8n
│   │   └── workflows/
│   ├── airflow/             # Uses: airflow
│   │   └── dags/
│   └── windmill/            # Uses: windmill
│       └── scripts/
└── config/
    └── automation.yaml      # Shared automation config
```
