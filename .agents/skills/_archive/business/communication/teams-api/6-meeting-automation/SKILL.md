---
name: teams-api-6-meeting-automation
description: 'Sub-skill of teams-api: 6. Meeting Automation.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 6. Meeting Automation

## 6. Meeting Automation


```python
# meetings.py
# ABOUTME: Teams meeting automation via Graph API
# ABOUTME: Create, manage, and get meeting details

from datetime import datetime, timedelta
from typing import List, Optional, Dict
import asyncio

class MeetingManager:
    """Manage Teams meetings via Graph API"""

    def __init__(self, graph_client):
        self.client = graph_client

    async def create_instant_meeting(
        self,
        subject: str,
        organizer_id: str
    ) -> Dict:
        """Create an instant meeting"""

        from msgraph.generated.models.online_meeting import OnlineMeeting

        meeting = OnlineMeeting(
            subject=subject,
            start_date_time=datetime.utcnow().isoformat() + "Z",
            end_date_time=(datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
        )

        result = await self.client.users.by_user_id(organizer_id) \
            .online_meetings.post(meeting)

        return {
            "join_url": result.join_web_url,
            "meeting_id": result.id,
            "subject": result.subject
        }

    async def schedule_meeting(
        self,
        subject: str,
        start_time: datetime,
        end_time: datetime,
        organizer_id: str,
        attendee_emails: List[str],
        body: str = ""
    ) -> Dict:
        """Schedule a meeting with attendees"""

        from msgraph.generated.models.event import Event
        from msgraph.generated.models.item_body import ItemBody
        from msgraph.generated.models.body_type import BodyType
        from msgraph.generated.models.attendee import Attendee
        from msgraph.generated.models.email_address import EmailAddress
        from msgraph.generated.models.attendee_type import AttendeeType
        from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone

        attendees = [
            Attendee(
                email_address=EmailAddress(address=email),
                type=AttendeeType.Required
            )
            for email in attendee_emails
        ]

        event = Event(
            subject=subject,
            body=ItemBody(
                content_type=BodyType.Html,
                content=body
            ),
            start=DateTimeTimeZone(
                date_time=start_time.isoformat(),
                time_zone="UTC"
            ),
            end=DateTimeTimeZone(
                date_time=end_time.isoformat(),
                time_zone="UTC"
            ),
            attendees=attendees,
            is_online_meeting=True,
            online_meeting_provider="teamsForBusiness"
        )

        result = await self.client.users.by_user_id(organizer_id) \
            .events.post(event)

        return {
            "event_id": result.id,
            "subject": result.subject,
            "join_url": result.online_meeting.join_url if result.online_meeting else None
        }

    async def get_user_calendar(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get user's calendar events"""

        result = await self.client.users.by_user_id(user_id) \
            .calendar_view.get(
                request_configuration=lambda config: (
                    setattr(config.query_parameters, 'start_date_time', start_date.isoformat()),
                    setattr(config.query_parameters, 'end_date_time', end_date.isoformat())
                )
            )

        return [
            {
                "id": event.id,
                "subject": event.subject,
                "start": event.start.date_time,
                "end": event.end.date_time,
                "is_online": event.is_online_meeting
            }
            for event in result.value
        ]

    async def cancel_meeting(
        self,
        user_id: str,
        event_id: str,
        cancellation_message: str = ""
    ):
        """Cancel a scheduled meeting"""

        await self.client.users.by_user_id(user_id) \
            .events.by_event_id(event_id) \
            .cancel.post(comment=cancellation_message)

# Usage example
async def schedule_standup():
    """Schedule a daily standup meeting"""

    from graph_client import TeamsGraphClient

    client = TeamsGraphClient()
    meetings = MeetingManager(client.client)

    # Schedule for tomorrow at 9 AM
    tomorrow = datetime.utcnow().replace(hour=9, minute=0) + timedelta(days=1)

    result = await meetings.schedule_meeting(
        subject="Daily Standup",
        start_time=tomorrow,
        end_time=tomorrow + timedelta(minutes=30),
        organizer_id="organizer@company.com",
        attendee_emails=[
            "team-member1@company.com",
            "team-member2@company.com"
        ],
        body="<h2>Daily Standup</h2><p>Please be prepared to share your updates.</p>"
    )

    print(f"Meeting scheduled: {result['join_url']}")
```
