---
name: todoist-api-1-projects-management
description: 'Sub-skill of todoist-api: 1. Projects Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Projects Management

## 1. Projects Management


**REST API - Projects:**
```bash
# List all projects
curl -s -X GET "https://api.todoist.com/rest/v2/projects" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Get specific project
curl -s -X GET "https://api.todoist.com/rest/v2/projects/PROJECT_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Create project
curl -s -X POST "https://api.todoist.com/rest/v2/projects" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Work Tasks",
        "color": "blue",
        "is_favorite": true,
        "view_style": "list"
    }' | jq

# Create sub-project
curl -s -X POST "https://api.todoist.com/rest/v2/projects" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Q1 Goals",
        "parent_id": "PARENT_PROJECT_ID",
        "color": "green"
    }' | jq

# Update project
curl -s -X POST "https://api.todoist.com/rest/v2/projects/PROJECT_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Work Tasks - Updated",
        "color": "red"
    }' | jq

# Delete project
curl -s -X DELETE "https://api.todoist.com/rest/v2/projects/PROJECT_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY"

# Get project collaborators
curl -s -X GET "https://api.todoist.com/rest/v2/projects/PROJECT_ID/collaborators" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq
```

**Python SDK - Projects:**
```python
from todoist_api_python import TodoistAPI
import os

api = TodoistAPI(os.environ["TODOIST_API_KEY"])

# List all projects
projects = api.get_projects()
for project in projects:
    print(f"{project.name} (ID: {project.id})")

# Get specific project
project = api.get_project(project_id="2345678901")
print(f"Project: {project.name}, Color: {project.color}")

# Create project
new_project = api.add_project(
    name="New Project",
    color="blue",
    is_favorite=True,
    view_style="board"  # "list" or "board"
)
print(f"Created: {new_project.name} (ID: {new_project.id})")

# Create sub-project
sub_project = api.add_project(
    name="Sub Project",
    parent_id="2345678901",
    color="green"
)

# Update project
updated = api.update_project(
    project_id="2345678901",
    name="Updated Name",
    color="red"
)

# Delete project
api.delete_project(project_id="2345678901")

# Get project sections
sections = api.get_sections(project_id="2345678901")
for section in sections:
    print(f"  Section: {section.name}")
```
