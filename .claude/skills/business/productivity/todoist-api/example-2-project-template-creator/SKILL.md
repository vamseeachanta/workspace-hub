---
name: todoist-api-example-2-project-template-creator
description: 'Sub-skill of todoist-api: Example 2: Project Template Creator (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Example 2: Project Template Creator (+1)

## Example 2: Project Template Creator


```python
#!/usr/bin/env python3
"""project_template.py - Create projects from templates"""

from todoist_api_python import TodoistAPI
import os
import json

api = TodoistAPI(os.environ["TODOIST_API_KEY"])


*See sub-skills for full details.*

## Example 3: Daily Task Report


```python
#!/usr/bin/env python3
"""daily_report.py - Generate daily task report"""

from todoist_api_python import TodoistAPI
from datetime import datetime
import os

api = TodoistAPI(os.environ["TODOIST_API_KEY"])


*See sub-skills for full details.*
