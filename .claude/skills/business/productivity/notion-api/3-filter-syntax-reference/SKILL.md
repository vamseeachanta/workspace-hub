---
name: notion-api-3-filter-syntax-reference
description: 'Sub-skill of notion-api: 3. Filter Syntax Reference.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 3. Filter Syntax Reference

## 3. Filter Syntax Reference


**Text Filters:**
```python
# Text property filters
{"property": "Name", "title": {"equals": "Exact Match"}}
{"property": "Name", "title": {"does_not_equal": "Not This"}}
{"property": "Name", "title": {"contains": "partial"}}
{"property": "Name", "title": {"does_not_contain": "exclude"}}
{"property": "Name", "title": {"starts_with": "Prefix"}}
{"property": "Name", "title": {"ends_with": "suffix"}}
{"property": "Name", "title": {"is_empty": True}}
{"property": "Name", "title": {"is_not_empty": True}}

# Rich text property
{"property": "Notes", "rich_text": {"contains": "keyword"}}
```

**Number Filters:**
```python
{"property": "Amount", "number": {"equals": 100}}
{"property": "Amount", "number": {"does_not_equal": 0}}
{"property": "Amount", "number": {"greater_than": 50}}
{"property": "Amount", "number": {"less_than": 100}}
{"property": "Amount", "number": {"greater_than_or_equal_to": 10}}
{"property": "Amount", "number": {"less_than_or_equal_to": 99}}
{"property": "Amount", "number": {"is_empty": True}}
{"property": "Amount", "number": {"is_not_empty": True}}
```

**Date Filters:**
```python
{"property": "Due Date", "date": {"equals": "2025-01-17"}}
{"property": "Due Date", "date": {"before": "2025-01-20"}}
{"property": "Due Date", "date": {"after": "2025-01-10"}}
{"property": "Due Date", "date": {"on_or_before": "2025-01-17"}}
{"property": "Due Date", "date": {"on_or_after": "2025-01-01"}}
{"property": "Due Date", "date": {"is_empty": True}}
{"property": "Due Date", "date": {"is_not_empty": True}}

# Relative date filters
{"property": "Due Date", "date": {"past_week": {}}}
{"property": "Due Date", "date": {"past_month": {}}}
{"property": "Due Date", "date": {"past_year": {}}}
{"property": "Due Date", "date": {"next_week": {}}}
{"property": "Due Date", "date": {"next_month": {}}}
{"property": "Due Date", "date": {"next_year": {}}}
{"property": "Due Date", "date": {"this_week": {}}}
```

**Select/Multi-Select Filters:**
```python
# Select
{"property": "Status", "select": {"equals": "Done"}}
{"property": "Status", "select": {"does_not_equal": "Done"}}
{"property": "Status", "select": {"is_empty": True}}
{"property": "Status", "select": {"is_not_empty": True}}

# Multi-select
{"property": "Tags", "multi_select": {"contains": "urgent"}}
{"property": "Tags", "multi_select": {"does_not_contain": "archived"}}
{"property": "Tags", "multi_select": {"is_empty": True}}
{"property": "Tags", "multi_select": {"is_not_empty": True}}
```

**Checkbox Filters:**
```python
{"property": "Completed", "checkbox": {"equals": True}}
{"property": "Completed", "checkbox": {"equals": False}}
```

**Relation and Rollup Filters:**
```python
# Relation
{"property": "Project", "relation": {"contains": "page-id"}}
{"property": "Project", "relation": {"does_not_contain": "page-id"}}
{"property": "Project", "relation": {"is_empty": True}}
{"property": "Project", "relation": {"is_not_empty": True}}

# Rollup (depends on rollup type)
{"property": "Total Tasks", "rollup": {"number": {"greater_than": 5}}}
{"property": "Completion", "rollup": {"number": {"equals": 100}}}
```

**Compound Filters:**
```python
# AND
{
    "and": [
        {"property": "Status", "select": {"equals": "In Progress"}},
        {"property": "Priority", "select": {"equals": "High"}},
        {"property": "Due Date", "date": {"before": "2025-02-01"}}
    ]
}

# OR
{
    "or": [
        {"property": "Status", "select": {"equals": "To Do"}},
        {"property": "Status", "select": {"equals": "In Progress"}}
    ]
}

# Nested (AND with OR)
{
    "and": [
        {
            "or": [
                {"property": "Priority", "select": {"equals": "High"}},
                {"property": "Priority", "select": {"equals": "Medium"}}
            ]
        },
        {"property": "Status", "select": {"does_not_equal": "Done"}}
    ]
}
```
