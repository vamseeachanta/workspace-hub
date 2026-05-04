---
name: todoist-api-3-labels-management
description: 'Sub-skill of todoist-api: 3. Labels Management (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 3. Labels Management (+1)

## 3. Labels Management


**REST API - Labels:**
```bash
# List all labels
curl -s -X GET "https://api.todoist.com/rest/v2/labels" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Create label
curl -s -X POST "https://api.todoist.com/rest/v2/labels" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "urgent",
        "color": "red",
        "order": 1,
        "is_favorite": true
    }' | jq

# Update label
curl -s -X POST "https://api.todoist.com/rest/v2/labels/LABEL_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "high-priority",
        "color": "orange"
    }' | jq

# Delete label
curl -s -X DELETE "https://api.todoist.com/rest/v2/labels/LABEL_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY"
```

**Python SDK - Labels:**
```python
from todoist_api_python import TodoistAPI

api = TodoistAPI(os.environ["TODOIST_API_KEY"])

# List all labels
labels = api.get_labels()
for label in labels:
    print(f"@{label.name} (color: {label.color})")

# Create label
new_label = api.add_label(
    name="review",
    color="blue",
    order=1,
    is_favorite=True
)

# Update label
api.update_label(
    label_id=new_label.id,
    name="code-review",
    color="green"
)

# Delete label
api.delete_label(label_id=new_label.id)

# Get tasks with specific label
review_tasks = api.get_tasks(filter="@code-review")
```


## 4. Sections Management


**REST API - Sections:**
```bash
# List sections for project
curl -s -X GET "https://api.todoist.com/rest/v2/sections?project_id=PROJECT_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Create section
curl -s -X POST "https://api.todoist.com/rest/v2/sections" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "In Progress",
        "project_id": "PROJECT_ID",
        "order": 2
    }' | jq

# Update section
curl -s -X POST "https://api.todoist.com/rest/v2/sections/SECTION_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Currently Working"
    }' | jq

# Delete section
curl -s -X DELETE "https://api.todoist.com/rest/v2/sections/SECTION_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY"
```

**Python SDK - Sections:**
```python
# Create Kanban-style sections
sections = ["Backlog", "To Do", "In Progress", "Review", "Done"]

for i, section_name in enumerate(sections):
    api.add_section(
        name=section_name,
        project_id="2345678901",
        order=i
    )

# Get sections
sections = api.get_sections(project_id="2345678901")
for section in sections:
    print(f"Section: {section.name} (ID: {section.id})")

# Move task to section
api.update_task(
    task_id="1234567890",
    section_id="IN_PROGRESS_SECTION_ID"
)
```
