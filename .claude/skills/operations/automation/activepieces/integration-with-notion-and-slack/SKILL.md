---
name: activepieces-integration-with-notion-and-slack
description: 'Sub-skill of activepieces: Integration with Notion and Slack.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Integration with Notion and Slack

## Integration with Notion and Slack


```typescript
const notionSlackSync = {
  "displayName": "Notion to Slack Sync",
  "trigger": {
    "name": "notion_database_updated",
    "type": "PIECE_TRIGGER",
    "settings": {
      "pieceName": "@activepieces/piece-notion",
      "triggerName": "database_item_updated",
      "input": {
        "database_id": "{{connections.notion.task_database_id}}"
      }
    },
    "displayName": "Task Updated in Notion"
  },
  "steps": [
    {
      "name": "check_status_change",
      "type": "CODE",
      "settings": {
        "input": {
          "item": "{{trigger}}"
        },
        "sourceCode": {
          "code": `
export const code = async (inputs) => {
  const { item } = inputs;

  const statusProperty = item.properties?.Status;
  const currentStatus = statusProperty?.select?.name;

  return {
    task_name: item.properties?.Name?.title?.[0]?.plain_text || 'Unnamed Task',
    status: currentStatus,
    assignee: item.properties?.Assignee?.people?.[0]?.name || 'Unassigned',
    due_date: item.properties?.['Due Date']?.date?.start,
    url: item.url,
    is_completed: currentStatus === 'Done',
    is_blocked: currentStatus === 'Blocked'
  };
};`
        }
      },
      "displayName": "Extract Task Details"
    },
    {
      "name": "route_notification",
      "type": "BRANCH",
      "settings": {
        "conditions": [
          {
            "name": "task_completed",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{check_status_change.is_completed}} === true"
            },
            "steps": [
              {
                "name": "celebrate_completion",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-slack",
                  "actionName": "send_message",
                  "input": {
                    "channel": "#team-wins",
                    "text": "Task completed! {{check_status_change.task_name}} by {{check_status_change.assignee}}"
                  }
                }
              }
            ]
          },
          {
            "name": "task_blocked",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{check_status_change.is_blocked}} === true"
            },
            "steps": [
              {
                "name": "alert_blockers",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-slack",
                  "actionName": "send_message",
                  "input": {
                    "channel": "#blockers",
                    "text": "Task blocked: {{check_status_change.task_name}} - Assigned to {{check_status_change.assignee}}"
                  }
                }
              }
            ]
          }
        ]
      },
      "displayName": "Route Notification"
    }
  ]
};
```
