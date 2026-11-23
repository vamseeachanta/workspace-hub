---
name: gitbook-github-actions-for-git-sync
description: 'Sub-skill of gitbook: GitHub Actions for Git Sync (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# GitHub Actions for Git Sync (+1)

## GitHub Actions for Git Sync


```yaml
# .github/workflows/gitbook-sync.yml
name: Sync to GitBook

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'SUMMARY.md'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Validate Structure
        run: |
          # Check required files exist
          test -f docs/README.md || echo "Missing docs/README.md"
          test -f docs/SUMMARY.md || echo "Missing docs/SUMMARY.md"

          # Check for broken links
          python3 << 'EOF'
          import re
          from pathlib import Path

          summary = Path("docs/SUMMARY.md").read_text()
          links = re.findall(r'\[.*?\]\((.*?\.md)\)', summary)

          for link in links:
              path = Path("docs") / link
              if not path.exists():
                  print(f"Broken link: {link}")
                  exit(1)

          print("All links valid!")
          EOF

      - name: Notify on Success
        if: success()
        run: |
          echo "Documentation synced successfully!"
          # GitBook automatically pulls from connected repo
```


## Slack Notification for Updates


```python
#!/usr/bin/env python3
"""slack_notify.py - Notify Slack of GitBook updates"""

import os
import requests
from datetime import datetime, timedelta

def notify_docs_update(space_title, update_type, details):
    """Send Slack notification for docs update."""
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Documentation Update: {space_title}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Type:*\n{update_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{details}"
                }
            }
        ]
    }

    response = requests.post(webhook_url, json=message)
    return response.status_code == 200
```
