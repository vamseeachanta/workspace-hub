---
name: documentation-integration-with-workspace-hub
description: 'Sub-skill of documentation: Integration with Workspace-Hub.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Integration with Workspace-Hub

## Integration with Workspace-Hub


These skills power documentation across the workspace:

```
workspace-hub/
├── docs/
│   ├── mkdocs.yml           # Uses: mkdocs
│   └── src/
│       ├── index.md
│       └── guides/
├── presentations/
│   └── slides.md            # Uses: marp
├── scripts/
│   ├── build-docs.sh        # Uses: mkdocs, sphinx
│   ├── convert-docs.sh      # Uses: pandoc
│   └── generate-api.sh      # Uses: sphinx autodoc
└── .github/workflows/
    └── docs.yml             # CI/CD for documentation
```
