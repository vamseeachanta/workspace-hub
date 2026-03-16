---
name: notion-api-common-issues
description: 'Sub-skill of notion-api: Common Issues.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: 401 Unauthorized**
```python
# Verify API key
curl -s "https://api.notion.com/v1/users/me" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28"

# Check if integration is connected to the page/database
# Go to page > ... menu > Connections > Your integration
```

**Issue: 404 Not Found**
```python
# Ensure integration has access to the page
# The integration must be explicitly connected to each page

# For databases, check the database ID is correct
# Database ID format: 32 hex characters (with or without hyphens)
```

**Issue: 400 Bad Request**
```python
# Check property names match exactly (case-sensitive)
# Verify property types match the database schema

# Common mistakes:
# - Using "title" instead of actual title property name
# - Wrong select/multi_select option names
# - Invalid date format (use ISO 8601: "2025-01-17")
```

**Issue: Rate limiting (429)**
```python
# Notion allows ~3 requests/second
# Implement exponential backoff
# Check Retry-After header for wait time
```
