---
name: calendly-api-3-scheduled-events
description: 'Sub-skill of calendly-api: 3. Scheduled Events.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 3. Scheduled Events

## 3. Scheduled Events


```python
# scheduled_events.py
# ABOUTME: Scheduled event management
# ABOUTME: List, retrieve, and cancel scheduled events

from client import client
from typing import Optional, List
from datetime import datetime, timedelta


def list_scheduled_events(
    user_uri: str = None,
    organization_uri: str = None,
    min_start_time: str = None,
    max_start_time: str = None,
    status: str = "active",
    invitee_email: str = None,
    sort: str = "start_time:asc",
) -> list:
    """List scheduled events

    status: active, canceled
    sort: start_time:asc, start_time:desc
    """
    params = {
        "status": status,
        "sort": sort,
    }

    if user_uri:
        params["user"] = user_uri
    elif organization_uri:
        params["organization"] = organization_uri
    else:
        params["user"] = client.user_uri

    if min_start_time:
        params["min_start_time"] = min_start_time
    if max_start_time:
        params["max_start_time"] = max_start_time
    if invitee_email:
        params["invitee_email"] = invitee_email

    return client.paginate("/scheduled_events", params=params)


def get_scheduled_event(event_uri: str) -> dict:
    """Get scheduled event details"""
    uuid = event_uri.split("/")[-1]
    response = client.get(f"/scheduled_events/{uuid}")
    return response.get("resource", {})


def cancel_scheduled_event(event_uri: str, reason: str = None) -> dict:
    """Cancel a scheduled event"""
    uuid = event_uri.split("/")[-1]
    data = {}
    if reason:
        data["reason"] = reason

    response = client.post(f"/scheduled_events/{uuid}/cancellation", json=data)
    return response.get("resource", {})


def get_upcoming_events(
    user_uri: str = None,
    days_ahead: int = 7,
) -> list:
    """Get upcoming events for the next N days"""
    now = datetime.utcnow()
    end = now + timedelta(days=days_ahead)

    return list_scheduled_events(
        user_uri=user_uri,
        min_start_time=now.isoformat() + "Z",
        max_start_time=end.isoformat() + "Z",
        status="active",
    )


def get_past_events(
    user_uri: str = None,
    days_back: int = 30,
) -> list:
    """Get past events from the last N days"""
    now = datetime.utcnow()
    start = now - timedelta(days=days_back)

    return list_scheduled_events(
        user_uri=user_uri,
        min_start_time=start.isoformat() + "Z",
        max_start_time=now.isoformat() + "Z",
        status="active",
        sort="start_time:desc",
    )


def format_event_summary(event: dict) -> dict:
    """Format event for display"""
    return {
        "uri": event.get("uri"),
        "name": event.get("name"),
        "start_time": event.get("start_time"),
        "end_time": event.get("end_time"),
        "status": event.get("status"),
        "location": event.get("location", {}).get("type"),
        "event_type": event.get("event_type"),
        "guests_count": len(event.get("event_guests", [])),
        "cancellation": event.get("cancellation"),
    }


def get_events_by_email(email: str, user_uri: str = None) -> list:
    """Find all events with a specific invitee email"""
    return list_scheduled_events(
        user_uri=user_uri,
        invitee_email=email,
    )


if __name__ == "__main__":
    # Get upcoming events
    events = get_upcoming_events(days_ahead=14)

    print(f"Upcoming events: {len(events)}")
    for event in events:
        summary = format_event_summary(event)
        print(f"  - {summary['name']} at {summary['start_time']}")

    # Get events for specific invitee
    email_events = get_events_by_email("john@example.com")
    print(f"\nEvents with john@example.com: {len(email_events)}")
```
