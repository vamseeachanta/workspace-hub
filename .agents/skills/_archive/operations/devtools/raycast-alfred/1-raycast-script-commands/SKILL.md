---
name: raycast-alfred-1-raycast-script-commands
description: 'Sub-skill of raycast-alfred: 1. Raycast Script Commands.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Raycast Script Commands

## 1. Raycast Script Commands


```bash
#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Open Project
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 📁
# @raycast.argument1 { "type": "text", "placeholder": "Project name", "optional": false }
# @raycast.packageName Developer Tools

# Documentation:
# @raycast.description Opens a project in VS Code
# @raycast.author Your Name
# @raycast.authorURL https://github.com/yourname

PROJECT="$1"
PROJECT_DIR="$HOME/projects/$PROJECT"

if [ -d "$PROJECT_DIR" ]; then
    code "$PROJECT_DIR"
    echo "Opened $PROJECT"
else
    echo "Project not found: $PROJECT"
    exit 1
fi
```

```bash
#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Git Status
# @raycast.mode fullOutput
# @raycast.icon 🔀
# @raycast.packageName Git

# @raycast.description Show git status for current directory
# @raycast.author workspace-hub

cd "$(pwd)" || exit 1

if [ -d ".git" ]; then
    echo "Branch: $(git branch --show-current)"
    echo ""
    echo "Status:"
    git status --short
    echo ""
    echo "Recent commits:"
    git log --oneline -5
else
    echo "Not a git repository"
    exit 1
fi
```

```python
#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title UUID Generator
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🔑
# @raycast.argument1 { "type": "dropdown", "placeholder": "Format", "data": [{"title": "Standard", "value": "standard"}, {"title": "No dashes", "value": "nodash"}, {"title": "Uppercase", "value": "upper"}] }
# @raycast.packageName Utilities

import uuid
import subprocess
import sys

format_type = sys.argv[1] if len(sys.argv) > 1 else "standard"

new_uuid = str(uuid.uuid4())

if format_type == "nodash":
    new_uuid = new_uuid.replace("-", "")
elif format_type == "upper":
    new_uuid = new_uuid.upper()

# Copy to clipboard
subprocess.run(["pbcopy"], input=new_uuid.encode(), check=True)

print(f"Copied: {new_uuid}")
```

```bash
#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Kill Port
# @raycast.mode compact
# @raycast.icon 🔌
# @raycast.argument1 { "type": "text", "placeholder": "Port number" }
# @raycast.packageName Developer Tools

PORT="$1"

# Find process on port
PID=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PID" ]; then
    echo "No process on port $PORT"
    exit 0
fi

# Kill the process
kill -9 $PID 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Killed process $PID on port $PORT"
else
    echo "Failed to kill process on port $PORT"
    exit 1
fi
```
