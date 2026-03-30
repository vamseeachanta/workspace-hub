---
name: calendly-api-5-webhooks
description: 'Sub-skill of calendly-api: 5. Webhooks.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 5. Webhooks

## 5. Webhooks


```python
# webhooks.py
# ABOUTME: Webhook subscription management
# ABOUTME: Create, manage, and handle webhook events

from client import client
import hmac
import hashlib
from typing import Optional, List


def list_webhook_subscriptions(
    organization_uri: str = None,
    user_uri: str = None,
    scope: str = None,
) -> list:
    """List webhook subscriptions

    scope: organization, user
    """
    params = {}

    if organization_uri:
        params["organization"] = organization_uri
    elif user_uri:
        params["user"] = user_uri
    else:
        params["organization"] = client.organization_uri

    if scope:
        params["scope"] = scope

    return client.paginate("/webhook_subscriptions", params=params)


def create_webhook_subscription(
    url: str,
    events: list,
    organization_uri: str = None,
    user_uri: str = None,
    signing_key: str = None,
) -> dict:
    """Create a webhook subscription

    events: invitee.created, invitee.canceled, routing_form_submission.created
    """
    data = {
        "url": url,
        "events": events,
    }

    if organization_uri:
        data["organization"] = organization_uri
        data["scope"] = "organization"
    elif user_uri:
        data["user"] = user_uri
        data["scope"] = "user"
    else:
        data["organization"] = client.organization_uri
        data["scope"] = "organization"

    if signing_key:
        data["signing_key"] = signing_key

    response = client.post("/webhook_subscriptions", json=data)
    return response.get("resource", {})


def get_webhook_subscription(subscription_uri: str) -> dict:
    """Get webhook subscription details"""
    uuid = subscription_uri.split("/")[-1]
    response = client.get(f"/webhook_subscriptions/{uuid}")
    return response.get("resource", {})


def delete_webhook_subscription(subscription_uri: str) -> bool:
    """Delete a webhook subscription"""
    uuid = subscription_uri.split("/")[-1]
    client.delete(f"/webhook_subscriptions/{uuid}")
    return True


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    signing_key: str,
    tolerance: int = 180,
) -> bool:
    """Verify Calendly webhook signature

    Calendly uses HMAC-SHA256 for webhook signatures
    """
    import time

    # Parse signature header
    # Format: t=timestamp,v1=signature
    parts = dict(p.split("=", 1) for p in signature.split(","))

    timestamp = int(parts.get("t", 0))
    expected_sig = parts.get("v1", "")

    # Check timestamp tolerance
    if abs(time.time() - timestamp) > tolerance:
        return False

    # Compute expected signature
    signed_payload = f"{timestamp}.{payload.decode()}"
    computed_sig = hmac.new(
        signing_key.encode(),
        signed_payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed_sig, expected_sig)


# Webhook event types
WEBHOOK_EVENTS = {
    "invitee.created": "When a new invitee schedules an event",
    "invitee.canceled": "When an invitee cancels an event",
    "routing_form_submission.created": "When a routing form is submitted",
}


class WebhookHandler:
    """Handler for Calendly webhook events"""

    def __init__(self, signing_key: str = None):
        self.signing_key = signing_key
        self.handlers = {}

    def on(self, event: str):
        """Decorator to register an event handler"""
        def decorator(func):
            self.handlers[event] = func
            return func
        return decorator

    def handle(self, payload: dict) -> dict:
        """Handle an incoming webhook event"""
        event = payload.get("event")
        data = payload.get("payload", {})

        handler = self.handlers.get(event)
        if handler:
            return handler(data)

        return {"handled": False, "event": event}


# Example webhook handler
webhook = WebhookHandler()


@webhook.on("invitee.created")
def handle_new_booking(data: dict) -> dict:
    """Handle new booking webhook"""
    invitee = data.get("invitee", {})
    event = data.get("scheduled_event", {})

    return {
        "handled": True,
        "action": "booking_created",
        "invitee_email": invitee.get("email"),
        "event_name": event.get("name"),
        "start_time": event.get("start_time"),
    }


@webhook.on("invitee.canceled")
def handle_cancellation(data: dict) -> dict:
    """Handle cancellation webhook"""
    invitee = data.get("invitee", {})
    cancellation = invitee.get("cancellation", {})

    return {
        "handled": True,
        "action": "booking_canceled",
        "invitee_email": invitee.get("email"),
        "reason": cancellation.get("reason"),
        "canceled_by": cancellation.get("canceled_by"),
    }



*Content truncated — see parent skill for full reference.*
