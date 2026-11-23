---
name: trello-api-trello-with-github-actions
description: 'Sub-skill of trello-api: Trello with GitHub Actions (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Trello with GitHub Actions (+1)

## Trello with GitHub Actions


```yaml
# .github/workflows/trello-sync.yml
name: Sync Issues to Trello

on:
  issues:
    types: [opened, labeled]

jobs:
  create-card:
    runs-on: ubuntu-latest
    steps:
      - name: Create Trello Card
        env:
          TRELLO_API_KEY: ${{ secrets.TRELLO_API_KEY }}
          TRELLO_TOKEN: ${{ secrets.TRELLO_TOKEN }}
          TRELLO_LIST_ID: ${{ secrets.TRELLO_LIST_ID }}
        run: |
          curl -s -X POST "https://api.trello.com/1/cards" \
            -d "key=$TRELLO_API_KEY" \
            -d "token=$TRELLO_TOKEN" \
            -d "idList=$TRELLO_LIST_ID" \
            -d "name=${{ github.event.issue.title }}" \
            -d "desc=${{ github.event.issue.body }}" \
            -d "urlSource=${{ github.event.issue.html_url }}"
```


## Trello with Slack


```python
#!/usr/bin/env python3
"""trello_slack_integration.py - Notify Slack on Trello updates"""

import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

@app.route("/webhook/trello", methods=["HEAD", "POST"])
def trello_webhook():
    if request.method == "HEAD":
        return "", 200

    data = request.json
    action = data.get("action", {})
    action_type = action.get("type")

    # Build Slack message
    message = None

    if action_type == "createCard":
        card = action["data"]["card"]
        list_name = action["data"]["list"]["name"]
        member = action["memberCreator"]["fullName"]

        message = {
            "text": f"New card created by {member}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New Card Created*\n"
                                f"*Card:* {card['name']}\n"
                                f"*List:* {list_name}\n"
                                f"*By:* {member}"
                    }
                }
            ]
        }

    elif action_type == "updateCard" and "listAfter" in action["data"]:
        card = action["data"]["card"]
        list_before = action["data"]["listBefore"]["name"]
        list_after = action["data"]["listAfter"]["name"]
        member = action["memberCreator"]["fullName"]

        message = {
            "text": f"Card moved by {member}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Card Moved*\n"
                                f"*Card:* {card['name']}\n"
                                f"*From:* {list_before} -> *To:* {list_after}\n"
                                f"*By:* {member}"
                    }
                }
            ]
        }

    if message:
        requests.post(SLACK_WEBHOOK_URL, json=message)

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=5000)
```
