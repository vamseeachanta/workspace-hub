---
name: obsidian-integration-with-todoist
description: 'Sub-skill of obsidian: Integration with Todoist.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Integration with Todoist

## Integration with Todoist


```python
#!/usr/bin/env python3
"""sync_todoist_obsidian.py - Sync Todoist tasks to Obsidian"""

import os
import json
from datetime import datetime
from todoist_api_python import TodoistAPI

TODOIST_API_KEY = os.environ.get("TODOIST_API_KEY")

*See sub-skills for full details.*
