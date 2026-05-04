---
name: calendly-api-2-event-types
description: 'Sub-skill of calendly-api: 2. Event Types.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 2. Event Types

## 2. Event Types


```python
# event_types.py
# ABOUTME: Event type management
# ABOUTME: Create, list, and configure event types

from client import client
from typing import Optional, List


def list_event_types(
    user_uri: str = None,
    organization_uri: str = None,
    active: bool = True,
) -> list:
    """List all event types for a user or organization"""
    params = {}

    if user_uri:
        params["user"] = user_uri
    elif organization_uri:
        params["organization"] = organization_uri
    else:
        params["user"] = client.user_uri

    if active is not None:
        params["active"] = str(active).lower()

    return client.paginate("/event_types", params=params)


def get_event_type(event_type_uri: str) -> dict:
    """Get event type details"""
    uuid = event_type_uri.split("/")[-1]
    response = client.get(f"/event_types/{uuid}")
    return response.get("resource", {})


def get_event_type_by_slug(slug: str, user_uri: str = None) -> Optional[dict]:
    """Find event type by slug"""
    event_types = list_event_types(user_uri=user_uri)

    for et in event_types:
        if et.get("slug") == slug:
            return et

    return None


def get_available_times(
    event_type_uri: str,
    start_time: str,
    end_time: str,
) -> list:
    """Get available time slots for an event type

    Times should be ISO 8601 format: 2026-01-17T00:00:00Z
    """
    params = {
        "event_type": event_type_uri,
        "start_time": start_time,
        "end_time": end_time,
    }
    response = client.get("/event_type_available_times", params=params)
    return response.get("collection", [])


def format_event_type_summary(event_type: dict) -> dict:
    """Format event type for display"""
    return {
        "name": event_type.get("name"),
        "slug": event_type.get("slug"),
        "duration": event_type.get("duration"),
        "scheduling_url": event_type.get("scheduling_url"),
        "type": event_type.get("type"),  # StandardEventType, AdhocEventType
        "kind": event_type.get("kind"),  # solo, round_robin, collective
        "active": event_type.get("active"),
        "description": event_type.get("description_plain"),
    }


def list_event_types_summary(user_uri: str = None) -> list:
    """Get summarized list of event types"""
    event_types = list_event_types(user_uri=user_uri)
    return [format_event_type_summary(et) for et in event_types]


if __name__ == "__main__":
    # List all event types
    event_types = list_event_types_summary()

    print("Available Event Types:")
    for et in event_types:
        status = "Active" if et["active"] else "Inactive"
        print(f"  - {et['name']} ({et['duration']} min) [{status}]")
        print(f"    URL: {et['scheduling_url']}")

    # Get available times for an event type
    if event_types:
        et_uri = event_types[0].get("uri")
        from datetime import datetime, timedelta

        start = datetime.now().isoformat() + "Z"
        end = (datetime.now() + timedelta(days=7)).isoformat() + "Z"

        times = get_available_times(et_uri, start, end)
        print(f"\nAvailable slots: {len(times)}")
```
