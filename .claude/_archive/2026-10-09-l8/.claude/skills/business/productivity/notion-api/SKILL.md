---
name: notion-api
version: 1.0.0
description: Notion API for workspace automation including databases, pages, blocks,
  query/filter syntax, and integration patterns
author: workspace-hub
category: business
type: skill
capabilities:
- database_operations
- page_management
- block_manipulation
- query_filtering
- property_types
- relation_rollups
- search_api
- integration_patterns
tools:
- notion-api
- notion-client
- curl
- jq
tags:
- notion
- api
- databases
- pages
- blocks
- automation
- productivity
- workspace
- integration
platforms:
- rest-api
- python
- javascript
- web
related_skills:
- api-integration
- todoist-api
- obsidian
requires: []
scripts_exempt: true
---

# Notion Api

## When to Use This Skill

### USE Notion API when:

- Automating database entries and updates
- Building custom dashboards from Notion data
- Syncing data between Notion and external systems
- Creating pages programmatically from templates
- Querying databases with complex filters
- Building integrations with other productivity tools
- Generating reports from Notion databases
- Implementing workflow automations
### DON'T USE Notion API when:

- Need real-time sync (API has rate limits)
- Building chat/messaging features (use Slack API)
- Need file storage solution (use dedicated storage)
- Simple task management only (use Todoist API)
- Need offline-first solution (use Obsidian)
- Require sub-second response times

## Prerequisites

### Create Integration

```markdown
1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name: "My Integration"
4. Select workspace
5. Set capabilities (Read/Write content, etc.)
6. Copy the "Internal Integration Token"
```
### Connect Integration to Pages

```markdown
1. Open the Notion page/database you want to access
2. Click "..." menu (top right)
3. Click "Connections" > "Connect to" > Your integration
4. Integration can now access this page and children
```
### Environment Setup

```bash
# Set environment variable
export NOTION_API_KEY="secret_xxxxxxxxxxxxxxxxxxxxx"

# Verify connection
curl -s "https://api.notion.com/v1/users/me" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" | jq
```
### Python SDK Installation

```bash
# Install official Python client
pip install notion-client

# Or with uv
uv pip install notion-client

# Additional dependencies
pip install python-dotenv requests
```
### Verify Setup

```python
from notion_client import Client
import os

notion = Client(auth=os.environ["NOTION_API_KEY"])

# Test connection
me = notion.users.me()
print(f"Connected as: {me['name']}")

# List accessible databases
databases = notion.search(filter={"property": "object", "value": "database"})
print(f"Found {len(databases['results'])} databases")
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-17 | Initial release with comprehensive Notion API coverage |

## Resources

- [Notion API Documentation](https://developers.notion.com/)
- [API Reference](https://developers.notion.com/reference/intro)
- [Python SDK](https://github.com/ramnes/notion-sdk-py)
- [JavaScript SDK](https://github.com/makenotion/notion-sdk-js)
- [Integration Gallery](https://www.notion.so/integrations)
- [API Changelog](https://developers.notion.com/changelog)

---

*This skill enables powerful workspace automation through Notion's comprehensive API, supporting databases, pages, blocks, queries, and integration patterns.*

## Sub-Skills

- [1. Database Operations](1-database-operations/SKILL.md)
- [2. Query Databases](2-query-databases/SKILL.md)
- [3. Filter Syntax Reference](3-filter-syntax-reference/SKILL.md)
- [4. Page Operations](4-page-operations/SKILL.md)
- [5. Block Operations](5-block-operations/SKILL.md)
- [6. Rich Text Formatting (+1)](6-rich-text-formatting/SKILL.md)
- [8. Search API](8-search-api/SKILL.md)
- [Integration with Slack (+1)](integration-with-slack/SKILL.md)
- [1. Rate Limiting (+3)](1-rate-limiting/SKILL.md)
- [Common Issues](common-issues/SKILL.md)

## Sub-Skills

- [Example 1: Task Management System (+2)](example-1-task-management-system/SKILL.md)
