---
name: slack-api-6-webhooks-and-incoming-messages
description: 'Sub-skill of slack-api: 6. Webhooks and Incoming Messages.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 6. Webhooks and Incoming Messages

## 6. Webhooks and Incoming Messages


```python
# webhooks.py
# ABOUTME: Incoming webhook integration for external services
# ABOUTME: CI/CD notifications, alerts, and external triggers

import requests
import json
from typing import Optional, List, Dict
import hmac
import hashlib
import time

class SlackWebhook:
    """Incoming webhook client for Slack"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(
        self,
        text: str,
        blocks: Optional[List[Dict]] = None,
        attachments: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
        unfurl_links: bool = True,
        unfurl_media: bool = True
    ) -> dict:
        """Send a message via webhook"""

        payload = {
            "text": text,
            "unfurl_links": unfurl_links,
            "unfurl_media": unfurl_media
        }

        if blocks:
            payload["blocks"] = blocks
        if attachments:
            payload["attachments"] = attachments
        if thread_ts:
            payload["thread_ts"] = thread_ts

        response = requests.post(
            self.webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        response.raise_for_status()
        return {"ok": True, "status": response.status_code}

    def send_deployment_notification(
        self,
        app_name: str,
        environment: str,
        version: str,
        status: str,
        commit_sha: str,
        author: str,
        url: Optional[str] = None
    ):
        """Send a deployment notification"""

        color_map = {
            "success": "#36a64f",
            "failure": "#ff0000",
            "started": "#ffcc00",
            "pending": "#808080"
        }

        status_emoji = {
            "success": ":white_check_mark:",
            "failure": ":x:",
            "started": ":rocket:",
            "pending": ":hourglass:"
        }

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji.get(status, ':grey_question:')} Deployment {status.title()}: {app_name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Environment:*\n{environment}"},
                    {"type": "mrkdwn", "text": f"*Version:*\n{version}"},
                    {"type": "mrkdwn", "text": f"*Commit:*\n`{commit_sha[:8]}`"},
                    {"type": "mrkdwn", "text": f"*Author:*\n{author}"}
                ]
            }
        ]

        if url:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Deployment"},
                        "url": url,
                        "style": "primary" if status == "success" else None
                    }
                ]
            })

        attachments = [
            {
                "color": color_map.get(status, "#808080"),
                "blocks": blocks
            }
        ]

        return self.send(
            text=f"Deployment {status}: {app_name} to {environment}",
            attachments=attachments
        )

    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        source: str = "System",
        details: Optional[Dict] = None
    ):
        """Send an alert notification"""

        severity_config = {
            "critical": {"emoji": ":rotating_light:", "color": "#ff0000"},
            "error": {"emoji": ":x:", "color": "#ff4444"},
            "warning": {"emoji": ":warning:", "color": "#ffcc00"},
            "info": {"emoji": ":information_source:", "color": "#0088ff"}
        }

        config = severity_config.get(severity, severity_config["info"])

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{config['emoji']} {title}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message}
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"*Source:* {source} | *Severity:* {severity.upper()}"}
                ]
            }
        ]

        if details:
            detail_text = "\n".join(f"*{k}:* {v}" for k, v in details.items())
            blocks.insert(2, {
                "type": "section",
                "text": {"type": "mrkdwn", "text": detail_text}
            })

        return self.send(
            text=f"[{severity.upper()}] {title}",
            attachments=[{"color": config["color"], "blocks": blocks}]
        )

# Webhook signature verification
def verify_slack_signature(
    signing_secret: str,
    request_body: str,
    timestamp: str,
    signature: str
) -> bool:
    """Verify Slack request signature"""

    # Check timestamp to prevent replay attacks

*Content truncated — see parent skill for full reference.*
