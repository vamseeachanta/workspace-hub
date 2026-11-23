---
name: teams-api-1-microsoft-graph-api-client
description: 'Sub-skill of teams-api: 1. Microsoft Graph API Client.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Microsoft Graph API Client

## 1. Microsoft Graph API Client


```python
# graph_client.py
# ABOUTME: Microsoft Graph API client for Teams operations
# ABOUTME: Handles authentication and common API calls

from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
import os
from dotenv import load_dotenv

load_dotenv()

class TeamsGraphClient:
    """Microsoft Graph client for Teams operations"""

    def __init__(self):
        self.credential = ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"]
        )

        self.client = GraphServiceClient(
            credentials=self.credential,
            scopes=["https://graph.microsoft.com/.default"]
        )

    async def send_channel_message(
        self,
        team_id: str,
        channel_id: str,
        content: str,
        content_type: str = "html"
    ):
        """Send a message to a Teams channel"""

        message = ChatMessage(
            body=ItemBody(
                content_type=BodyType.Html if content_type == "html" else BodyType.Text,
                content=content
            )
        )

        result = await self.client.teams.by_team_id(team_id) \
            .channels.by_channel_id(channel_id) \
            .messages.post(message)

        return result

    async def send_chat_message(
        self,
        chat_id: str,
        content: str
    ):
        """Send a message to a chat (1:1 or group)"""

        message = ChatMessage(
            body=ItemBody(
                content_type=BodyType.Html,
                content=content
            )
        )

        result = await self.client.chats.by_chat_id(chat_id) \
            .messages.post(message)

        return result

    async def list_teams(self):
        """List all teams the app has access to"""
        result = await self.client.groups.get()
        teams = [g for g in result.value if g.resource_provisioning_options
                 and "Team" in g.resource_provisioning_options]
        return teams

    async def list_channels(self, team_id: str):
        """List channels in a team"""
        result = await self.client.teams.by_team_id(team_id) \
            .channels.get()
        return result.value

    async def get_channel_messages(
        self,
        team_id: str,
        channel_id: str,
        top: int = 50
    ):
        """Get recent messages from a channel"""

        result = await self.client.teams.by_team_id(team_id) \
            .channels.by_channel_id(channel_id) \
            .messages.get(
                request_configuration=lambda config:
                    setattr(config.query_parameters, 'top', top)
            )

        return result.value

    async def reply_to_message(
        self,
        team_id: str,
        channel_id: str,
        message_id: str,
        content: str
    ):
        """Reply to a channel message"""

        reply = ChatMessage(
            body=ItemBody(
                content_type=BodyType.Html,
                content=content
            )
        )

        result = await self.client.teams.by_team_id(team_id) \
            .channels.by_channel_id(channel_id) \
            .messages.by_chat_message_id(message_id) \
            .replies.post(reply)

        return result

    async def create_online_meeting(
        self,
        subject: str,
        start_time: str,
        end_time: str,
        attendees: list
    ):
        """Create an online meeting"""
        from msgraph.generated.models.online_meeting import OnlineMeeting
        from msgraph.generated.models.meeting_participants import MeetingParticipants
        from msgraph.generated.models.meeting_participant_info import MeetingParticipantInfo
        from msgraph.generated.models.identity_set import IdentitySet
        from msgraph.generated.models.identity import Identity

        participant_list = [
            MeetingParticipantInfo(
                identity=IdentitySet(
                    user=Identity(id=attendee)
                )
            )
            for attendee in attendees
        ]

        meeting = OnlineMeeting(
            subject=subject,
            start_date_time=start_time,
            end_date_time=end_time,
            participants=MeetingParticipants(
                attendees=participant_list
            )
        )

        result = await self.client.me.online_meetings.post(meeting)
        return result

    async def get_user_by_email(self, email: str):
        """Get user details by email"""
        result = await self.client.users.by_user_id(email).get()
        return result

# Usage example
async def main():
    client = TeamsGraphClient()

    # List teams
    teams = await client.list_teams()
    for team in teams:
        print(f"Team: {team.display_name} ({team.id})")

    # Send channel message
    if teams:
        team_id = teams[0].id
        channels = await client.list_channels(team_id)
        if channels:
            channel_id = channels[0].id
            await client.send_channel_message(
                team_id,
                channel_id,
                "<b>Hello from Python!</b> This is an automated message."
            )

*Content truncated — see parent skill for full reference.*
