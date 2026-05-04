---
name: notion-api-integration-with-slack
description: 'Sub-skill of notion-api: Integration with Slack (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Integration with Slack (+1)

## Integration with Slack


```python
#!/usr/bin/env python3
"""slack_notion.py - Sync Slack messages to Notion"""

import os
import requests
from notion_client import Client

notion = Client(auth=os.environ["NOTION_API_KEY"])
SLACK_WEBHOOK = os.environ["SLACK_WEBHOOK_URL"]

def notify_slack_on_page_update(page_id, message):
    """Send Slack notification when Notion page is updated"""
    page = notion.pages.retrieve(page_id)
    title = page["properties"]["Name"]["title"][0]["plain_text"]

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Notion Update*: {title}\n{message}"
                }
            },
            {
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View in Notion"},
                    "url": page["url"]
                }]
            }
        ]
    }

    requests.post(SLACK_WEBHOOK, json=payload)

def create_notion_page_from_slack(database_id, title, content, channel):
    """Create Notion page from Slack message"""
    return notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {"title": [{"text": {"content": title}}]},
            "Source": {"select": {"name": "Slack"}},
            "Channel": {"rich_text": [{"text": {"content": channel}}]}
        },
        children=[{
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": content}}]
            }
        }]
    )
```


## Integration with GitHub


```python
#!/usr/bin/env python3
"""github_notion.py - Sync GitHub issues to Notion"""

import os
import requests
from notion_client import Client

notion = Client(auth=os.environ["NOTION_API_KEY"])
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

def sync_github_issues_to_notion(repo, database_id):
    """Sync GitHub issues to Notion database"""
    # Fetch issues from GitHub
    response = requests.get(
        f"https://api.github.com/repos/{repo}/issues",
        headers={"Authorization": f"token {GITHUB_TOKEN}"}
    )
    issues = response.json()

    for issue in issues:
        # Check if issue already exists in Notion
        existing = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "GitHub ID",
                "number": {"equals": issue["number"]}
            }
        )

        properties = {
            "Name": {"title": [{"text": {"content": issue["title"]}}]},
            "GitHub ID": {"number": issue["number"]},
            "Status": {
                "select": {"name": "Open" if issue["state"] == "open" else "Closed"}
            },
            "URL": {"url": issue["html_url"]},
            "Labels": {
                "multi_select": [{"name": l["name"]} for l in issue["labels"]]
            }
        }

        if existing["results"]:
            # Update existing
            notion.pages.update(
                page_id=existing["results"][0]["id"],
                properties=properties
            )
        else:
            # Create new
            notion.pages.create(
                parent={"database_id": database_id},
                properties=properties,
                children=[{
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": issue.get("body", "") or ""}}]
                    }
                }]
            )

    print(f"Synced {len(issues)} issues from {repo}")
```
