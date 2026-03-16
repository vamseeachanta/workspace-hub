---
name: notion-api-8-search-api
description: 'Sub-skill of notion-api: 8. Search API.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 8. Search API

## 8. Search API


**Search Operations:**
```python
# Search all
results = notion.search()
print(f"Total accessible items: {len(results['results'])}")

# Search with query
results = notion.search(query="project plan")
for item in results["results"]:
    obj_type = item["object"]
    if obj_type == "page":
        title = item["properties"].get("title", {}).get("title", [{}])[0].get("plain_text", "Untitled")
    elif obj_type == "database":
        title = item["title"][0]["plain_text"] if item["title"] else "Untitled"
    print(f"{obj_type}: {title}")

# Search only pages
results = notion.search(
    query="meeting",
    filter={"property": "object", "value": "page"}
)

# Search only databases
results = notion.search(
    filter={"property": "object", "value": "database"}
)

# Search with sorting
results = notion.search(
    query="report",
    sort={
        "direction": "descending",
        "timestamp": "last_edited_time"
    }
)

# Paginated search
def search_all(query=None, filter=None):
    """Search with pagination"""
    all_results = []
    has_more = True
    start_cursor = None

    while has_more:
        response = notion.search(
            query=query,
            filter=filter,
            start_cursor=start_cursor,
            page_size=100
        )
        all_results.extend(response["results"])
        has_more = response["has_more"]
        start_cursor = response.get("next_cursor")

    return all_results
```
