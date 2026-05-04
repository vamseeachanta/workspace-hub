---
name: todoist-api-2-tasks-management
description: 'Sub-skill of todoist-api: 2. Tasks Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 2. Tasks Management

## 2. Tasks Management


**REST API - Tasks:**
```bash
# List all tasks
curl -s -X GET "https://api.todoist.com/rest/v2/tasks" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Get tasks with filter
curl -s -X GET "https://api.todoist.com/rest/v2/tasks?filter=today" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Get tasks for specific project
curl -s -X GET "https://api.todoist.com/rest/v2/tasks?project_id=PROJECT_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Get single task
curl -s -X GET "https://api.todoist.com/rest/v2/tasks/TASK_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Create task with all options
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "Complete project report",
        "description": "Include Q4 metrics and projections",
        "project_id": "PROJECT_ID",
        "section_id": "SECTION_ID",
        "parent_id": null,
        "order": 1,
        "labels": ["work", "urgent"],
        "priority": 4,
        "due_string": "tomorrow at 5pm",
        "due_lang": "en",
        "assignee_id": null
    }' | jq

# Create task with natural language due date
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "Weekly review",
        "due_string": "every friday at 4pm"
    }' | jq

# Update task
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/TASK_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "Updated task content",
        "priority": 3,
        "due_string": "next monday"
    }' | jq

# Complete task
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/TASK_ID/close" \
    -H "Authorization: Bearer $TODOIST_API_KEY"

# Reopen task
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/TASK_ID/reopen" \
    -H "Authorization: Bearer $TODOIST_API_KEY"

# Delete task
curl -s -X DELETE "https://api.todoist.com/rest/v2/tasks/TASK_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY"
```

**Python SDK - Tasks:**
```python
from todoist_api_python import TodoistAPI
from datetime import datetime, timedelta
import os

api = TodoistAPI(os.environ["TODOIST_API_KEY"])

# Get all tasks
tasks = api.get_tasks()
for task in tasks:
    due = task.due.string if task.due else "No due date"
    print(f"- [{task.priority}] {task.content} (Due: {due})")

# Get tasks with filter
today_tasks = api.get_tasks(filter="today")
overdue_tasks = api.get_tasks(filter="overdue")
high_priority = api.get_tasks(filter="p1 | p2")

# Get tasks for project
project_tasks = api.get_tasks(project_id="2345678901")

# Create task
new_task = api.add_task(
    content="Review pull requests",
    description="Check all open PRs in main repo",
    project_id="2345678901",
    section_id="3456789012",
    labels=["work", "development"],
    priority=4,  # 1=normal, 2=medium, 3=high, 4=urgent
    due_string="tomorrow at 10am",
    due_lang="en"
)
print(f"Created task: {new_task.id}")

# Create sub-task
sub_task = api.add_task(
    content="Review frontend PR #123",
    parent_id=new_task.id,
    priority=3
)

# Create recurring task
recurring_task = api.add_task(
    content="Weekly team standup",
    due_string="every monday at 9am"
)

# Update task
updated_task = api.update_task(
    task_id=new_task.id,
    content="Review all pull requests",
    priority=4,
    due_string="today at 5pm"
)

# Complete task
api.close_task(task_id=new_task.id)

# Reopen task
api.reopen_task(task_id=new_task.id)

# Delete task
api.delete_task(task_id=new_task.id)

# Move task to different project
api.update_task(
    task_id="1234567890",
    project_id="NEW_PROJECT_ID"
)
```
