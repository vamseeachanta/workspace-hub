---
name: slack-api-2-block-kit-messages
description: 'Sub-skill of slack-api: 2. Block Kit Messages.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 2. Block Kit Messages

## 2. Block Kit Messages


```python
# blocks.py
# ABOUTME: Block Kit message construction utilities
# ABOUTME: Creates rich, interactive Slack messages

from slack_bolt import App
import os

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def create_deployment_message(
    environment: str,
    version: str,
    status: str,
    deploy_url: str,
    logs_url: str
) -> list:
    """Create a deployment notification with Block Kit"""

    status_emoji = {
        "success": ":white_check_mark:",
        "failure": ":x:",
        "in_progress": ":hourglass_flowing_sand:",
        "pending": ":clock3:"
    }

    emoji = status_emoji.get(status, ":question:")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} Deployment {status.title()}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Environment:*\n{environment}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Version:*\n{version}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{status.title()}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Time:*\n<!date^{int(time.time())}^{{date_short}} at {{time}}|now>"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Deployment",
                        "emoji": True
                    },
                    "url": deploy_url,
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Logs",
                        "emoji": True
                    },
                    "url": logs_url
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Deployed by CI/CD Pipeline"
                }
            ]
        }
    ]

    return blocks

def create_approval_message(
    request_id: str,
    requester: str,
    description: str,
    details: dict
) -> list:
    """Create an approval request with interactive buttons"""

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":clipboard: Approval Request",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Request ID:* `{request_id}`\n*Requested by:* <@{requester}>\n\n{description}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Details:*\n" + "\n".join(
                    f"- {k}: {v}" for k, v in details.items()
                )
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "block_id": f"approval_{request_id}",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Approve",
                        "emoji": True
                    },
                    "style": "primary",
                    "action_id": "approve_request",
                    "value": request_id
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Reject",
                        "emoji": True
                    },
                    "style": "danger",
                    "action_id": "reject_request",
                    "value": request_id
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Request Info",
                        "emoji": True
                    },
                    "action_id": "request_info",
                    "value": request_id
                }
            ]
        }
    ]

    return blocks

def create_poll_message(question: str, options: list) -> list:
    """Create a poll with radio buttons"""

    option_elements = [
        {
            "text": {
                "type": "plain_text",
                "text": option,

*Content truncated — see parent skill for full reference.*
