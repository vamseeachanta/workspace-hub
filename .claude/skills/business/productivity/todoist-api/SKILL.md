---
name: todoist-api
version: 1.0.0
description: Task management API integration for Todoist with projects, tasks, labels,
  filters, webhooks, and Python SDK usage
author: workspace-hub
category: business
type: skill
capabilities:
- task_management
- project_organization
- label_filtering
- natural_language_dates
- recurring_tasks
- webhook_integration
- sync_api
- batch_operations
tools:
- todoist-api
- todoist-python
- curl
- jq
tags:
- todoist
- tasks
- api
- productivity
- gtd
- webhooks
- automation
- project-management
platforms:
- rest-api
- python
- web
- mobile
related_skills:
- api-integration
- obsidian
- notion-api
requires: []
scripts_exempt: true
---

# Todoist Api

## When to Use This Skill

### USE Todoist API when:

- Automating task creation from external systems
- Building integrations with other productivity tools
- Creating custom task dashboards or reports
- Implementing GTD workflows programmatically
- Syncing tasks with calendar applications
- Building CLI tools for task management
- Automating recurring task patterns
- Integrating with CI/CD for project tracking
### DON'T USE Todoist API when:

- Need complex project management (use Jira, Asana)
- Require database-style queries (use Notion API)
- Need real-time collaboration on tasks (use Linear)
- Building for enterprise with SSO requirements
- Need Gantt charts or resource management

## Prerequisites

### API Authentication

```bash
# Get your API token from:
# https://todoist.com/app/settings/integrations/developer

# Set environment variable
export TODOIST_API_KEY="your-api-token-here"

# Verify authentication
curl -s -X GET "https://api.todoist.com/rest/v2/projects" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq '.[0]'
```
### Python SDK Installation

```bash
# Install official Python SDK
pip install todoist-api-python

# Or with uv
uv pip install todoist-api-python

# For sync API features
pip install todoist-api-python requests
```
### Verify Setup

```python
from todoist_api_python import TodoistAPI

api = TodoistAPI("your-api-token")

# Test connection
try:
    projects = api.get_projects()
    print(f"Connected! Found {len(projects)} projects")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-17 | Initial release with comprehensive Todoist API coverage |

## Resources

- [Todoist REST API Documentation](https://developer.todoist.com/rest/v2/)
- [Todoist Sync API Documentation](https://developer.todoist.com/sync/v9/)
- [Todoist Python SDK](https://github.com/Doist/todoist-api-python)
- [Filter Query Syntax](https://todoist.com/help/articles/introduction-to-filters)
- [Webhook Events Reference](https://developer.todoist.com/sync/v9/#webhooks)

---

*This skill enables powerful task management automation through Todoist's comprehensive API, supporting projects, tasks, labels, filters, webhooks, and batch operations.*

## Sub-Skills

- [1. Projects Management](1-projects-management/SKILL.md)
- [2. Tasks Management](2-tasks-management/SKILL.md)
- [3. Labels Management (+1)](3-labels-management/SKILL.md)
- [5. Comments Management (+1)](5-comments-management/SKILL.md)
- [7. Sync API](7-sync-api/SKILL.md)
- [8. Webhooks](8-webhooks/SKILL.md)
- [Integration with Slack (+1)](integration-with-slack/SKILL.md)
- [1. Rate Limiting (+3)](1-rate-limiting/SKILL.md)
- [Common Issues](common-issues/SKILL.md)

## Sub-Skills

- [Example 1: GTD Weekly Review Automation](example-1-gtd-weekly-review-automation/SKILL.md)
- [Overdue Tasks ({len(report['overdue'])})](overdue-tasks-lenreportoverdue/SKILL.md)
- [Upcoming This Week ({len(report['upcoming'])})](upcoming-this-week-lenreportupcoming/SKILL.md)
- [Waiting For ({len(report['waiting_for'])})](waiting-for-lenreportwaitingfor/SKILL.md)
- [Example 2: Project Template Creator (+1)](example-2-project-template-creator/SKILL.md)
- [Summary](summary/SKILL.md)
- [Overdue Tasks](overdue-tasks/SKILL.md)
