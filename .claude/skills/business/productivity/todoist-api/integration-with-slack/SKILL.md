---
name: todoist-api-integration-with-slack
description: 'Sub-skill of todoist-api: Integration with Slack (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Integration with Slack (+1)

## Integration with Slack


```python
#!/usr/bin/env python3
"""slack_todoist.py - Post Todoist tasks to Slack"""

import os
import requests
from todoist_api_python import TodoistAPI

TODOIST_API_KEY = os.environ["TODOIST_API_KEY"]
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

api = TodoistAPI(TODOIST_API_KEY)

def post_daily_tasks_to_slack():
    """Post today's tasks to Slack"""
    tasks = api.get_tasks(filter="today")

    if not tasks:
        message = "No tasks due today!"
    else:
        task_list = "\n".join([f"- {t.content}" for t in tasks])
        message = f"*Tasks for Today ({len(tasks)}):*\n{task_list}"

    payload = {
        "text": message,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    return response.status_code == 200

if __name__ == "__main__":
    if post_daily_tasks_to_slack():
        print("Posted to Slack successfully")
    else:
        print("Failed to post to Slack")
```


## Integration with Calendar (Google Calendar)


```python
#!/usr/bin/env python3
"""calendar_sync.py - Sync Todoist tasks with Google Calendar"""

from todoist_api_python import TodoistAPI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

api = TodoistAPI(os.environ["TODOIST_API_KEY"])

def sync_tasks_to_calendar():
    """Sync tasks with due dates to Google Calendar"""
    creds = Credentials.from_authorized_user_file("token.json")
    service = build("calendar", "v3", credentials=creds)

    # Get tasks with due dates in next 7 days
    tasks = api.get_tasks(filter="next 7 days")

    for task in tasks:
        if not task.due:
            continue

        # Check if event already exists
        existing = find_existing_event(service, task.id)
        if existing:
            continue

        # Create calendar event
        event = {
            "summary": task.content,
            "description": f"Todoist Task ID: {task.id}\nPriority: {task.priority}",
            "start": {
                "date": task.due.date,
            },
            "end": {
                "date": task.due.date,
            },
            "extendedProperties": {
                "private": {
                    "todoist_id": task.id
                }
            }
        }

        service.events().insert(calendarId="primary", body=event).execute()
        print(f"Created calendar event: {task.content}")

def find_existing_event(service, todoist_id):
    """Find existing calendar event for Todoist task"""
    events = service.events().list(
        calendarId="primary",
        privateExtendedProperty=f"todoist_id={todoist_id}"
    ).execute()
    return events.get("items", [])
```
