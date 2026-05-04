---
name: calendly-api-4-invitees
description: 'Sub-skill of calendly-api: 4. Invitees.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 4. Invitees

## 4. Invitees


```python
# invitees.py
# ABOUTME: Invitee management for scheduled events
# ABOUTME: Retrieve invitee details and custom answers

from client import client
from typing import Optional, List


def list_invitees(
    event_uri: str,
    status: str = None,
    email: str = None,
) -> list:
    """List invitees for a scheduled event

    status: active, canceled
    """
    uuid = event_uri.split("/")[-1]
    params = {}

    if status:
        params["status"] = status
    if email:
        params["email"] = email

    return client.paginate(f"/scheduled_events/{uuid}/invitees", params=params)


def get_invitee(invitee_uri: str) -> dict:
    """Get invitee details"""
    # Parse invitee URI to get event and invitee UUIDs
    parts = invitee_uri.split("/")
    event_uuid = parts[-3]
    invitee_uuid = parts[-1]

    response = client.get(f"/scheduled_events/{event_uuid}/invitees/{invitee_uuid}")
    return response.get("resource", {})


def get_invitee_no_show(invitee_uri: str) -> Optional[dict]:
    """Get no-show status for an invitee"""
    parts = invitee_uri.split("/")
    invitee_uuid = parts[-1]

    try:
        response = client.get(f"/invitee_no_shows/{invitee_uuid}")
        return response.get("resource")
    except Exception:
        return None


def mark_invitee_no_show(invitee_uri: str) -> dict:
    """Mark an invitee as a no-show"""
    response = client.post("/invitee_no_shows", json={"invitee": invitee_uri})
    return response.get("resource", {})


def unmark_invitee_no_show(no_show_uri: str) -> bool:
    """Remove no-show status from an invitee"""
    uuid = no_show_uri.split("/")[-1]
    client.delete(f"/invitee_no_shows/{uuid}")
    return True


def format_invitee_summary(invitee: dict) -> dict:
    """Format invitee for display"""
    return {
        "uri": invitee.get("uri"),
        "name": invitee.get("name"),
        "email": invitee.get("email"),
        "status": invitee.get("status"),
        "timezone": invitee.get("timezone"),
        "created_at": invitee.get("created_at"),
        "rescheduled": invitee.get("rescheduled"),
        "questions_and_answers": [
            {
                "question": qa.get("question"),
                "answer": qa.get("answer"),
            }
            for qa in invitee.get("questions_and_answers", [])
        ],
        "tracking": invitee.get("tracking", {}),
        "utm_parameters": {
            "source": invitee.get("utm_source"),
            "medium": invitee.get("utm_medium"),
            "campaign": invitee.get("utm_campaign"),
        },
    }


def get_invitee_custom_answers(invitee: dict) -> dict:
    """Extract custom question answers from invitee"""
    answers = {}
    for qa in invitee.get("questions_and_answers", []):
        question = qa.get("question")
        answer = qa.get("answer")
        answers[question] = answer
    return answers


def get_all_invitees_for_events(event_uris: list) -> list:
    """Get invitees for multiple events"""
    all_invitees = []

    for event_uri in event_uris:
        invitees = list_invitees(event_uri)
        for invitee in invitees:
            invitee["event_uri"] = event_uri
        all_invitees.extend(invitees)

    return all_invitees


if __name__ == "__main__":
    from scheduled_events import get_upcoming_events

    # Get upcoming events and their invitees
    events = get_upcoming_events(days_ahead=7)

    for event in events[:5]:
        print(f"\nEvent: {event['name']}")
        invitees = list_invitees(event["uri"])

        for inv in invitees:
            summary = format_invitee_summary(inv)
            print(f"  - {summary['name']} ({summary['email']})")

            if summary["questions_and_answers"]:
                for qa in summary["questions_and_answers"]:
                    print(f"    Q: {qa['question']}")
                    print(f"    A: {qa['answer']}")
```
