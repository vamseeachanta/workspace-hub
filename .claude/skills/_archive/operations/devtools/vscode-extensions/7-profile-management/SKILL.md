---
name: vscode-extensions-7-profile-management
description: 'Sub-skill of vscode-extensions: 7. Profile Management.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 7. Profile Management

## 7. Profile Management


```bash
# Create profiles for different workflows
# Settings -> Profiles -> Create Profile

# Export profile
code --profile Python --export-default-profile > python-profile.json

# Import profile
code --profile Python --import-profile python-profile.json

# Switch profiles via command palette
# Cmd/Ctrl+Shift+P -> Profiles: Switch Profile

# Profile examples:
# - "Python" - Python extensions and settings
# - "Web" - JavaScript/TypeScript/React
# - "DevOps" - Docker, Kubernetes, YAML
# - "Minimal" - Basic editing only
# - "Writing" - Markdown, spell check
```
