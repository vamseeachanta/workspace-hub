---
name: notion-api-2-query-databases
description: 'Sub-skill of notion-api: 2. Query Databases.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 2. Query Databases

## 2. Query Databases


**Basic Query:**
```bash
# Query all items
curl -s -X POST "https://api.notion.com/v1/databases/DATABASE_ID/query" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d '{}' | jq '.results'

# Query with filter
curl -s -X POST "https://api.notion.com/v1/databases/DATABASE_ID/query" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d '{
        "filter": {
            "property": "Status",
            "select": {
                "equals": "In Progress"
            }
        }
    }' | jq '.results'

# Query with sort
curl -s -X POST "https://api.notion.com/v1/databases/DATABASE_ID/query" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d '{
        "sorts": [
            {
                "property": "Due Date",
                "direction": "ascending"
            }
        ]
    }' | jq '.results'
```

**Python - Query Operations:**
```python
# Simple query
results = notion.databases.query(database_id="your-database-id")
for page in results["results"]:
    props = page["properties"]
    name = props["Name"]["title"][0]["plain_text"] if props["Name"]["title"] else "Untitled"
    print(f"- {name}")

# Query with filter
results = notion.databases.query(
    database_id="your-database-id",
    filter={
        "property": "Status",
        "select": {
            "equals": "In Progress"
        }
    }
)

# Query with multiple filters (AND)
results = notion.databases.query(
    database_id="your-database-id",
    filter={
        "and": [
            {
                "property": "Status",
                "select": {"equals": "In Progress"}
            },
            {
                "property": "Priority",
                "select": {"equals": "High"}
            }
        ]
    }
)

# Query with OR filter
results = notion.databases.query(
    database_id="your-database-id",
    filter={
        "or": [
            {"property": "Status", "select": {"equals": "To Do"}},
            {"property": "Status", "select": {"equals": "In Progress"}}
        ]
    }
)

# Query with sorting
results = notion.databases.query(
    database_id="your-database-id",
    sorts=[
        {"property": "Priority", "direction": "ascending"},
        {"property": "Due Date", "direction": "ascending"}
    ]
)

# Paginated query
def query_all_pages(database_id, filter=None):
    """Query all pages with pagination"""
    all_results = []
    has_more = True
    start_cursor = None

    while has_more:
        response = notion.databases.query(
            database_id=database_id,
            filter=filter,
            start_cursor=start_cursor,
            page_size=100
        )
        all_results.extend(response["results"])
        has_more = response["has_more"]
        start_cursor = response.get("next_cursor")

    return all_results

all_items = query_all_pages("your-database-id")
print(f"Total items: {len(all_items)}")
```
