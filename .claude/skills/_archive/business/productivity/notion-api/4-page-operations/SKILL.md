---
name: notion-api-4-page-operations
description: 'Sub-skill of notion-api: 4. Page Operations.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 4. Page Operations

## 4. Page Operations


**Create Pages:**
```bash
# Create page in database
curl -s -X POST "https://api.notion.com/v1/pages" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d '{
        "parent": {"database_id": "DATABASE_ID"},
        "properties": {
            "Name": {
                "title": [{"text": {"content": "New Task"}}]
            },
            "Status": {
                "select": {"name": "To Do"}
            },
            "Priority": {
                "select": {"name": "High"}
            },
            "Due Date": {
                "date": {"start": "2025-01-20"}
            }
        }
    }' | jq
```

**Python - Page Operations:**
```python
# Create page in database
new_page = notion.pages.create(
    parent={"database_id": "your-database-id"},
    properties={
        "Name": {
            "title": [{"text": {"content": "New Task"}}]
        },
        "Status": {
            "select": {"name": "To Do"}
        },
        "Priority": {
            "select": {"name": "High"}
        },
        "Due Date": {
            "date": {"start": "2025-01-20", "end": "2025-01-25"}
        },
        "Tags": {
            "multi_select": [
                {"name": "development"},
                {"name": "urgent"}
            ]
        },
        "Assignee": {
            "people": [{"id": "user-id"}]
        },
        "Notes": {
            "rich_text": [{"text": {"content": "Task description here"}}]
        },
        "Completed": {
            "checkbox": False
        },
        "Amount": {
            "number": 100
        },
        "URL": {
            "url": "https://example.com"
        },
        "Email": {
            "email": "user@example.com"
        }
    }
)
print(f"Created page: {new_page['id']}")

# Create page with content (blocks)
new_page = notion.pages.create(
    parent={"database_id": "your-database-id"},
    properties={
        "Name": {"title": [{"text": {"content": "Page with Content"}}]}
    },
    children=[
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Overview"}}]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "This is the content."}}]
            }
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Task item"}}],
                "checked": False
            }
        }
    ]
)

# Retrieve page
page = notion.pages.retrieve(page_id="page-id")
print(f"Page: {page['properties']['Name']['title'][0]['plain_text']}")

# Update page properties
notion.pages.update(
    page_id="page-id",
    properties={
        "Status": {"select": {"name": "Done"}},
        "Completed": {"checkbox": True}
    }
)

# Archive page (soft delete)
notion.pages.update(
    page_id="page-id",
    archived=True
)

# Restore page
notion.pages.update(
    page_id="page-id",
    archived=False
)
```
