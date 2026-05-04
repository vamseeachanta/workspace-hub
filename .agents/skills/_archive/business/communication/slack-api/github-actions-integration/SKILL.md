---
name: slack-api-github-actions-integration
description: 'Sub-skill of slack-api: GitHub Actions Integration (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# GitHub Actions Integration (+1)

## GitHub Actions Integration


```yaml
# .github/workflows/slack-notify.yml
name: Slack Notifications

on:
  push:
    branches: [main]
  pull_request:
    types: [opened, closed, merged]
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  notify-deployment:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "blocks": [
                {
                  "type": "header",
                  "text": {
                    "type": "plain_text",
                    "text": ":rocket: Deployment Started"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {"type": "mrkdwn", "text": "*Repository:*\n${{ github.repository }}"},
                    {"type": "mrkdwn", "text": "*Branch:*\n${{ github.ref_name }}"},
                    {"type": "mrkdwn", "text": "*Commit:*\n`${{ github.sha }}`"},
                    {"type": "mrkdwn", "text": "*Author:*\n${{ github.actor }}"}
                  ]
                },
                {
                  "type": "actions",
                  "elements": [
                    {
                      "type": "button",
                      "text": {"type": "plain_text", "text": "View Commit"},
                      "url": "${{ github.event.head_commit.url }}"
                    }
                  ]
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```


## FastAPI Integration


```python
# api_integration.py
# ABOUTME: FastAPI integration for Slack event handling
# ABOUTME: Webhook endpoint for Slack Events API

from fastapi import FastAPI, Request, HTTPException
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
import os

# Initialize Slack app
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Register event handlers
@slack_app.event("message")
def handle_message(event, say):
    if "hello" in event.get("text", "").lower():
        say(f"Hi <@{event['user']}>!")

@slack_app.command("/api-status")
def handle_status(ack, respond):
    ack()
    respond("API is healthy!")

# FastAPI setup
app = FastAPI(title="Slack Bot API")
handler = SlackRequestHandler(slack_app)

@app.post("/slack/events")
async def slack_events(request: Request):
    """Handle Slack events"""
    return await handler.handle(request)

@app.post("/slack/interactions")
async def slack_interactions(request: Request):
    """Handle Slack interactive components"""
    return await handler.handle(request)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
```
