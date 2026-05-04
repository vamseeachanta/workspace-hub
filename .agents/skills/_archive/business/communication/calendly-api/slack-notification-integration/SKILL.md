---
name: calendly-api-slack-notification-integration
description: 'Sub-skill of calendly-api: Slack Notification Integration.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Slack Notification Integration

## Slack Notification Integration


```python
# slack_integration.py
# ABOUTME: Notify Slack when Calendly events are scheduled
# ABOUTME: Webhook handler with Slack notifications

import os
import requests
from flask import Flask, request, jsonify
from webhooks import WebhookHandler, verify_webhook_signature

app = Flask(__name__)
webhook = WebhookHandler(signing_key=os.environ.get("CALENDLY_WEBHOOK_SECRET"))

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")


def send_slack_notification(message: dict):
    """Send a message to Slack"""
    requests.post(SLACK_WEBHOOK_URL, json=message)


@webhook.on("invitee.created")
def handle_new_booking(data: dict) -> dict:
    """Notify Slack of new booking"""
    invitee = data.get("invitee", {})
    event = data.get("scheduled_event", {})
    event_type = data.get("event_type", {})

    # Extract custom answers
    answers = {}
    for qa in invitee.get("questions_and_answers", []):
        answers[qa["question"]] = qa["answer"]

    # Send Slack notification
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":calendar: New Meeting Scheduled",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Event:*\n{event_type.get('name')}"},
                {"type": "mrkdwn", "text": f"*Invitee:*\n{invitee.get('name')}"},
                {"type": "mrkdwn", "text": f"*Email:*\n{invitee.get('email')}"},
                {"type": "mrkdwn", "text": f"*Time:*\n{event.get('start_time')}"},
            ],
        },
    ]

    if answers:
        answer_text = "\n".join(f"*{q}:* {a}" for q, a in answers.items())
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Responses:*\n{answer_text}"},
        })

    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "View in Calendly"},
                "url": f"https://calendly.com/app/scheduled_events/{event['uri'].split('/')[-1]}",
            },
        ],
    })

    send_slack_notification({"blocks": blocks})

    return {"handled": True, "notified": "slack"}


@webhook.on("invitee.canceled")
def handle_cancellation(data: dict) -> dict:
    """Notify Slack of cancellation"""
    invitee = data.get("invitee", {})
    event = data.get("scheduled_event", {})
    cancellation = invitee.get("cancellation", {})

    send_slack_notification({
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":x: Meeting Canceled",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Event:*\n{event.get('name')}"},
                    {"type": "mrkdwn", "text": f"*Invitee:*\n{invitee.get('name')}"},
                    {"type": "mrkdwn", "text": f"*Reason:*\n{cancellation.get('reason', 'Not provided')}"},
                    {"type": "mrkdwn", "text": f"*Canceled by:*\n{cancellation.get('canceled_by')}"},
                ],
            },
        ],
    })

    return {"handled": True, "notified": "slack"}


@app.route("/webhooks/calendly", methods=["POST"])
def calendly_webhook():
    """Handle Calendly webhook"""
    # Verify signature
    signature = request.headers.get("Calendly-Webhook-Signature")
    if signature:
        signing_key = os.environ.get("CALENDLY_WEBHOOK_SECRET")
        if not verify_webhook_signature(request.data, signature, signing_key):
            return jsonify({"error": "Invalid signature"}), 401

    payload = request.json
    result = webhook.handle(payload)
    return jsonify(result)


if __name__ == "__main__":
    app.run(port=8080)
```
