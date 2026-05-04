---
name: notion-api-1-database-operations
description: 'Sub-skill of notion-api: 1. Database Operations.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Database Operations

## 1. Database Operations


**List and Search Databases:**
```bash
# Search for databases
curl -s -X POST "https://api.notion.com/v1/search" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d '{
        "filter": {
            "property": "object",
            "value": "database"
        }
    }' | jq '.results[] | {id: .id, title: .title[0].plain_text}'

# Get database schema
curl -s "https://api.notion.com/v1/databases/DATABASE_ID" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" | jq '.properties'
```

**Python - Database Operations:**
```python
from notion_client import Client
import os

notion = Client(auth=os.environ["NOTION_API_KEY"])

# Search for databases
results = notion.search(
    filter={"property": "object", "value": "database"}
)

for db in results["results"]:
    title = db["title"][0]["plain_text"] if db["title"] else "Untitled"
    print(f"Database: {title} (ID: {db['id']})")

# Get database details
database = notion.databases.retrieve(database_id="your-database-id")
print(f"Properties: {list(database['properties'].keys())}")

# Create database
new_db = notion.databases.create(
    parent={"type": "page_id", "page_id": "parent-page-id"},
    title=[{"type": "text", "text": {"content": "Tasks Database"}}],
    properties={
        "Name": {"title": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "To Do", "color": "gray"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Done", "color": "green"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "gray"}
                ]
            }
        },
        "Due Date": {"date": {}},
        "Assignee": {"people": {}},
        "Tags": {"multi_select": {"options": []}},
        "Completed": {"checkbox": {}},
        "Notes": {"rich_text": {}}
    }
)
print(f"Created database: {new_db['id']}")

# Update database
notion.databases.update(
    database_id="your-database-id",
    title=[{"type": "text", "text": {"content": "Updated Title"}}],
    properties={
        "New Property": {"rich_text": {}}
    }
)
```
