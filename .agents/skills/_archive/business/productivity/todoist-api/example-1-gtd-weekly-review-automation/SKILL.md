---
name: todoist-api-example-1-gtd-weekly-review-automation
description: 'Sub-skill of todoist-api: Example 1: GTD Weekly Review Automation.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Example 1: GTD Weekly Review Automation

## Example 1: GTD Weekly Review Automation


```python
#!/usr/bin/env python3
"""gtd_weekly_review.py - Automate GTD weekly review"""

from todoist_api_python import TodoistAPI
from datetime import datetime, timedelta
import os

api = TodoistAPI(os.environ["TODOIST_API_KEY"])


*See sub-skills for full details.*
