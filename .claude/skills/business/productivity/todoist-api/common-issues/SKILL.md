---
name: todoist-api-common-issues
description: 'Sub-skill of todoist-api: Common Issues.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: 401 Unauthorized**
```python
# Verify your API token
curl -s -X GET "https://api.todoist.com/rest/v2/projects" \
    -H "Authorization: Bearer $TODOIST_API_KEY"

# Check if token is set correctly
echo $TODOIST_API_KEY

# Regenerate token at:
# https://todoist.com/app/settings/integrations/developer
```

**Issue: 429 Too Many Requests**
```python
# Implement exponential backoff
import time

def retry_with_backoff(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e):
                wait = 2 ** i
                print(f"Rate limited, waiting {wait}s")
                time.sleep(wait)
            else:
                raise
```

**Issue: Task not appearing**
```python
# Check if task was created in different project
all_tasks = api.get_tasks()
for task in all_tasks:
    if "keyword" in task.content.lower():
        print(f"Found: {task.content} in project {task.project_id}")
```

**Issue: Due dates not parsing**
```python
# Use explicit date format
api.add_task(
    content="Test task",
    due_date="2025-01-20"  # ISO format
)

# Or use due_datetime for specific time
api.add_task(
    content="Test task",
    due_datetime="2025-01-20T14:00:00Z"  # ISO with time
)
```
