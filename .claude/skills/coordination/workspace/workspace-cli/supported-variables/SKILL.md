---
name: workspace-cli-supported-variables
description: 'Sub-skill of workspace-cli: Supported Variables (+1).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Supported Variables (+1)

## Supported Variables


```bash
# Default editor for config editing
export EDITOR=vim

# Log level
export LOG_LEVEL=INFO

# Parallel operations
export PARALLEL_JOBS=4
```


## Configuration File


Location: `config/workspace.conf`

```bash
# Workspace configuration
DEFAULT_SYNC_MESSAGE="Workspace sync"
PARALLEL_ENABLED=true
MAX_PARALLEL_JOBS=4
```
