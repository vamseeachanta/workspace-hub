---
name: time-tracking-time-tracking-with-github-actions
description: 'Sub-skill of time-tracking: Time Tracking with GitHub Actions (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Time Tracking with GitHub Actions (+1)

## Time Tracking with GitHub Actions


```yaml
# .github/workflows/log-time.yml
name: Log Development Time

on:
  push:
    branches: [main, develop]

jobs:
  log-time:
    runs-on: ubuntu-latest
    steps:
      - name: Log commit time to Toggl
        env:
          TOGGL_API_TOKEN: ${{ secrets.TOGGL_API_TOKEN }}
          TOGGL_WORKSPACE_ID: ${{ secrets.TOGGL_WORKSPACE_ID }}
          TOGGL_PROJECT_ID: ${{ secrets.TOGGL_PROJECT_ID }}
        run: |
          # Log 30 minute entry for each commit
          DESCRIPTION="Commit: ${{ github.event.head_commit.message }}"
          START_TIME=$(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S.000Z)

          curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
            -H "Content-Type: application/json" \
            "https://api.track.toggl.com/api/v9/workspaces/$TOGGL_WORKSPACE_ID/time_entries" \
            -d '{
              "created_with": "github_actions",
              "description": "'"${DESCRIPTION:0:100}"'",
              "workspace_id": '"$TOGGL_WORKSPACE_ID"',
              "project_id": '"$TOGGL_PROJECT_ID"',
              "start": "'"$START_TIME"'",
              "duration": 1800,
              "tags": ["github", "automated"]
            }'
```


## Slack Daily Summary


```python
#!/usr/bin/env python3
"""slack_time_summary.py - Post daily time summary to Slack"""

import os
import requests
from datetime import datetime, timedelta

def post_daily_summary(toggl_token, slack_webhook):
    """Post daily time summary to Slack."""
    toggl = TogglClient(toggl_token)

    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())

    entries = toggl.get_time_entries(start, end) or []

    total_hours = sum(
        e.get("duration", 0) / 3600
        for e in entries
        if e.get("duration", 0) > 0
    )

    # Build message
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Daily Time Summary - {today}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Hours:*\n{total_hours:.1f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Entries:*\n{len(entries)}"
                    }
                ]
            }
        ]
    }

    # Add top activities
    if entries:
        activities = "\n".join([
            f"- {e.get('description', 'No description')[:40]}: "
            f"{e.get('duration', 0)/3600:.1f}h"
            for e in sorted(entries, key=lambda x: x.get("duration", 0), reverse=True)[:5]
        ])

        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Top Activities:*\n{activities}"
            }
        })

    # Post to Slack
    response = requests.post(slack_webhook, json=message)
    return response.status_code == 200


if __name__ == "__main__":
    success = post_daily_summary(
        toggl_token=os.environ["TOGGL_API_TOKEN"],
        slack_webhook=os.environ["SLACK_WEBHOOK_URL"]
    )
    print("Posted to Slack" if success else "Failed to post")
```
