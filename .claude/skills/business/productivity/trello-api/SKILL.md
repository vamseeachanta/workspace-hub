---
name: trello-api
version: 1.0.0
description: Kanban board automation with Trello API including boards, lists, cards,
  members, webhooks, power-ups, and Python SDK (py-trello) integration
author: workspace-hub
category: business
type: skill
capabilities:
- Board creation and management
- List CRUD operations
- Card creation and manipulation
- Labels and checklists
- Member management
- Attachments and comments
- Webhook integration
- Power-up development
- Batch operations
- Custom fields
tools:
- trello-api
- py-trello
- curl
- jq
tags:
- trello
- kanban
- api
- productivity
- boards
- cards
- webhooks
- automation
- project-management
- py-trello
platforms:
- rest-api
- python
- web
related_skills:
- todoist-api
- notion-api
- api-integration
- github-actions
requires: []
see_also:
- trello-api-example-1-sprint-board-automation
- trello-api-sprint-goals
- trello-api-example-2-card-migration-tool
- trello-api-summary
- trello-api-cards-by-list
scripts_exempt: true
---

# Trello Api

## When to Use This Skill

### USE Trello API when:

- **Automating board management** - Create, update, archive boards programmatically
- **Building workflow integrations** - Connect Trello with other tools
- **Card automation** - Auto-create cards from external events
- **Progress tracking** - Build dashboards from Trello data
- **Notification systems** - React to board changes via webhooks
- **Bulk operations** - Move/update many cards at once
- **Custom reporting** - Extract data for analysis
- **Power-up development** - Extend Trello functionality
### DON'T USE Trello API when:

- **Need complex dependencies** - Use Jira or Asana
- **Require time tracking** - Built-in feature limited, use Toggl integration
- **Database-style queries** - Use Notion API instead
- **Enterprise compliance** - May need Enterprise-grade solutions
- **Complex workflows** - Consider Monday.com or Linear

## Prerequisites

### API Authentication

```bash
# Get API Key from:
# https://trello.com/app-key

# Get Token (authorize your app):
# https://trello.com/1/authorize?expiration=never&scope=read,write,account&response_type=token&name=MyApp&key=YOUR_API_KEY

# Set environment variables
export TRELLO_API_KEY="your-api-key"
export TRELLO_TOKEN="your-token"

# Verify authentication
curl -s "https://api.trello.com/1/members/me?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.fullName'
```
### Python SDK Installation

```bash
# Install py-trello
pip install py-trello

# Using uv (recommended)
uv pip install py-trello

# With additional dependencies
pip install py-trello requests python-dateutil

# Verify installation
python -c "from trello import TrelloClient; print('py-trello installed!')"
```
### Verify Setup

```python
from trello import TrelloClient
import os

client = TrelloClient(
    api_key=os.environ["TRELLO_API_KEY"],
    token=os.environ["TRELLO_TOKEN"]
)

# Test connection
me = client.get_member("me")
print(f"Connected as: {me.full_name}")
print(f"Username: {me.username}")
```

## Version History

- **1.0.0** (2026-01-17): Initial release
  - Board, list, card management
  - Labels and checklists
  - Member management
  - Webhook integration
  - Custom fields
  - Sprint automation example
  - Card migration tool
  - Board analytics
  - GitHub Actions integration
  - Slack integration

## Resources

- **Trello REST API**: https://developer.atlassian.com/cloud/trello/rest/
- **py-trello GitHub**: https://github.com/sarumont/py-trello
- **Trello Developer Portal**: https://developer.atlassian.com/cloud/trello/
- **Webhook Guide**: https://developer.atlassian.com/cloud/trello/guides/rest-api/webhooks/

---

**Automate your Kanban workflows with Trello API - boards, lists, cards, and beyond!**

## Sub-Skills

- [1. Board Management](1-board-management/SKILL.md)
- [2. List Management](2-list-management/SKILL.md)
- [3. Card Management](3-card-management/SKILL.md)
- [4. Labels Management (+1)](4-labels-management/SKILL.md)
- [6. Member Management](6-member-management/SKILL.md)
- [7. Webhooks](7-webhooks/SKILL.md)
- [8. Custom Fields](8-custom-fields/SKILL.md)
- [Trello with GitHub Actions (+1)](trello-with-github-actions/SKILL.md)
- [1. Use Batch Operations (+3)](1-use-batch-operations/SKILL.md)
- [Common Issues](common-issues/SKILL.md)

## Sub-Skills

- [Example 1: Sprint Board Automation](example-1-sprint-board-automation/SKILL.md)
- [Sprint Goals](sprint-goals/SKILL.md)
- [Example 2: Card Migration Tool (+1)](example-2-card-migration-tool/SKILL.md)
- [Summary](summary/SKILL.md)
- [Cards by List](cards-by-list/SKILL.md)
