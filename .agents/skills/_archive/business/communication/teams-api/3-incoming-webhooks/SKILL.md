---
name: teams-api-3-incoming-webhooks
description: 'Sub-skill of teams-api: 3. Incoming Webhooks.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 3. Incoming Webhooks

## 3. Incoming Webhooks


```python
# webhooks.py
# ABOUTME: Teams incoming webhook integration
# ABOUTME: Simple notifications without full bot registration

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class TeamsWebhook:
    """Incoming webhook client for Microsoft Teams"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(
        self,
        text: str = None,
        title: str = None,
        sections: List[Dict] = None,
        theme_color: str = None,
        adaptive_card: Dict = None
    ) -> dict:
        """Send a message via webhook"""

        if adaptive_card:
            # Send Adaptive Card
            payload = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "contentUrl": None,
                        "content": adaptive_card
                    }
                ]
            }
        else:
            # Send Message Card (legacy but simpler)
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": theme_color or "0076D7",
                "summary": title or text[:50] if text else "Notification"
            }

            if title:
                payload["title"] = title

            if text:
                payload["text"] = text

            if sections:
                payload["sections"] = sections

        response = requests.post(
            self.webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return {"ok": True, "status": response.status_code}
        else:
            return {
                "ok": False,
                "status": response.status_code,
                "error": response.text
            }

    def send_deployment_notification(
        self,
        app_name: str,
        environment: str,
        version: str,
        status: str,
        commit_sha: str,
        author: str,
        deploy_url: str = None,
        logs_url: str = None
    ):
        """Send a deployment notification"""

        theme_colors = {
            "success": "00FF00",
            "failure": "FF0000",
            "started": "FFCC00",
            "pending": "808080"
        }

        status_emoji = {
            "success": "OK",
            "failure": "X",
            "started": "ROCKET",
            "pending": "CLOCK"
        }

        sections = [
            {
                "activityTitle": f"Deployment {status.title()}: {app_name}",
                "activitySubtitle": f"by {author}",
                "facts": [
                    {"name": "Environment", "value": environment},
                    {"name": "Version", "value": version},
                    {"name": "Commit", "value": commit_sha[:8]},
                    {"name": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                ],
                "markdown": True
            }
        ]

        potential_actions = []
        if deploy_url:
            potential_actions.append({
                "@type": "OpenUri",
                "name": "View Deployment",
                "targets": [{"os": "default", "uri": deploy_url}]
            })
        if logs_url:
            potential_actions.append({
                "@type": "OpenUri",
                "name": "View Logs",
                "targets": [{"os": "default", "uri": logs_url}]
            })

        if potential_actions:
            sections[0]["potentialAction"] = potential_actions

        return self.send(
            title=f"Deployment {status.title()}",
            sections=sections,
            theme_color=theme_colors.get(status, "0076D7")
        )

    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        source: str = "System",
        details: Optional[Dict] = None,
        action_url: Optional[str] = None
    ):
        """Send an alert notification"""

        severity_colors = {
            "critical": "FF0000",
            "error": "FF4444",
            "warning": "FFCC00",
            "info": "0088FF"
        }

        facts = [
            {"name": "Severity", "value": severity.upper()},
            {"name": "Source", "value": source},
            {"name": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ]

        if details:
            for key, value in details.items():
                facts.append({"name": key, "value": str(value)})

        sections = [
            {
                "activityTitle": title,
                "text": message,
                "facts": facts,
                "markdown": True
            }
        ]

        if action_url:
            sections[0]["potentialAction"] = [
                {
                    "@type": "OpenUri",
                    "name": "View Details",
                    "targets": [{"os": "default", "uri": action_url}]
                }
            ]

        return self.send(
            title=title,
            sections=sections,

*Content truncated — see parent skill for full reference.*
