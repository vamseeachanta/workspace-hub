---
name: todoist-api-7-sync-api
description: 'Sub-skill of todoist-api: 7. Sync API.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 7. Sync API

## 7. Sync API


**Sync API Basics:**
```bash
# Initial sync (full read)
curl -s -X POST "https://api.todoist.com/sync/v9/sync" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "sync_token=*&resource_types=[\"all\"]" | jq

# Incremental sync (with sync token)
SYNC_TOKEN="your-sync-token-from-previous-response"
curl -s -X POST "https://api.todoist.com/sync/v9/sync" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "sync_token=$SYNC_TOKEN&resource_types=[\"items\",\"projects\"]" | jq

# Batch operations with commands
curl -s -X POST "https://api.todoist.com/sync/v9/sync" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "commands": [
            {
                "type": "item_add",
                "temp_id": "temp1",
                "uuid": "unique-uuid-1",
                "args": {
                    "content": "Task 1",
                    "project_id": "PROJECT_ID"
                }
            },
            {
                "type": "item_add",
                "temp_id": "temp2",
                "uuid": "unique-uuid-2",
                "args": {
                    "content": "Task 2",
                    "project_id": "PROJECT_ID"
                }
            }
        ]
    }' | jq
```

**Python Sync Operations:**
```python
import requests
import json
import uuid

TODOIST_API_KEY = os.environ["TODOIST_API_KEY"]
SYNC_URL = "https://api.todoist.com/sync/v9/sync"

def sync_read(sync_token="*", resource_types=None):
    """Read data using Sync API"""
    if resource_types is None:
        resource_types = ["all"]

    response = requests.post(
        SYNC_URL,
        headers={"Authorization": f"Bearer {TODOIST_API_KEY}"},
        data={
            "sync_token": sync_token,
            "resource_types": json.dumps(resource_types)
        }
    )
    return response.json()

def batch_add_tasks(tasks):
    """Add multiple tasks in one request"""
    commands = []
    for task in tasks:
        commands.append({
            "type": "item_add",
            "temp_id": f"temp_{uuid.uuid4().hex[:8]}",
            "uuid": str(uuid.uuid4()),
            "args": task
        })

    response = requests.post(
        SYNC_URL,
        headers={
            "Authorization": f"Bearer {TODOIST_API_KEY}",
            "Content-Type": "application/json"
        },
        json={"commands": commands}
    )
    return response.json()

# Example: Add multiple tasks at once
tasks_to_add = [
    {"content": "Task 1", "project_id": "2345678901", "priority": 4},
    {"content": "Task 2", "project_id": "2345678901", "priority": 3},
    {"content": "Task 3", "project_id": "2345678901", "priority": 2},
]

result = batch_add_tasks(tasks_to_add)
print(f"Added {len(tasks_to_add)} tasks")
```
