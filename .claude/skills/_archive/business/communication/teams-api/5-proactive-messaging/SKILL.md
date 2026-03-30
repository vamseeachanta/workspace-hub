---
name: teams-api-5-proactive-messaging
description: 'Sub-skill of teams-api: 5. Proactive Messaging.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 5. Proactive Messaging

## 5. Proactive Messaging


```python
# proactive.py
# ABOUTME: Send proactive messages to Teams channels and users
# ABOUTME: Notify users without them initiating conversation

from botbuilder.core import TurnContext
from botbuilder.core.teams import TeamsInfo
from botbuilder.schema import Activity, ConversationReference
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
import asyncio
from typing import Dict

class ProactiveMessenger:
    """Send proactive messages to Teams"""

    def __init__(
        self,
        adapter: CloudAdapter,
        app_id: str,
        conversation_references: Dict[str, ConversationReference]
    ):
        self.adapter = adapter
        self.app_id = app_id
        self.conversation_references = conversation_references

    async def send_to_conversation(
        self,
        conversation_id: str,
        message: str = None,
        card: Dict = None
    ):
        """Send a proactive message to a stored conversation"""

        if conversation_id not in self.conversation_references:
            raise ValueError(f"No conversation reference for {conversation_id}")

        conversation_reference = self.conversation_references[conversation_id]

        async def callback(turn_context: TurnContext):
            if card:
                from botbuilder.schema import Attachment
                from botbuilder.core import MessageFactory

                attachment = Attachment(
                    content_type="application/vnd.microsoft.card.adaptive",
                    content=card
                )
                await turn_context.send_activity(
                    MessageFactory.attachment(attachment)
                )
            else:
                await turn_context.send_activity(message)

        await self.adapter.continue_conversation(
            conversation_reference,
            callback,
            self.app_id
        )

    async def send_to_channel(
        self,
        service_url: str,
        team_id: str,
        channel_id: str,
        message: str = None,
        card: Dict = None
    ):
        """Send a proactive message to a Teams channel"""

        from botbuilder.schema import (
            ConversationParameters,
            Activity,
            ChannelAccount
        )

        # Create conversation reference for channel
        conversation_parameters = ConversationParameters(
            is_group=True,
            channel_data={"channel": {"id": channel_id}},
            activity=Activity(
                type="message",
                text=message
            ) if message else None
        )

        async def callback(turn_context: TurnContext):
            if card:
                from botbuilder.schema import Attachment
                from botbuilder.core import MessageFactory

                attachment = Attachment(
                    content_type="application/vnd.microsoft.card.adaptive",
                    content=card
                )
                await turn_context.send_activity(
                    MessageFactory.attachment(attachment)
                )
            elif message:
                await turn_context.send_activity(message)

        # Create and send the proactive message
        conversation_reference = ConversationReference(
            service_url=service_url,
            channel_id="msteams",
            conversation={"id": channel_id}
        )

        await self.adapter.continue_conversation(
            conversation_reference,
            callback,
            self.app_id
        )

    async def notify_all_conversations(
        self,
        message: str = None,
        card: Dict = None
    ):
        """Broadcast a message to all stored conversations"""

        for conv_id in self.conversation_references:
            try:
                await self.send_to_conversation(conv_id, message, card)
            except Exception as e:
                print(f"Failed to notify {conv_id}: {e}")

# Example usage with Azure Functions
"""
# function_app.py
import azure.functions as func
from proactive import ProactiveMessenger

async def notify_deployment_complete(req: func.HttpRequest) -> func.HttpResponse:
    # Load configuration and adapter
    messenger = ProactiveMessenger(adapter, app_id, conversation_references)

    card = create_deployment_card(
        app_name="my-service",
        environment="production",
        version="v1.2.3",
        status="success"
    )

    await messenger.send_to_channel(
        service_url="https://smba.trafficmanager.net/teams/",
        team_id="your-team-id",
        channel_id="your-channel-id",
        card=card
    )

    return func.HttpResponse("Notification sent", status_code=200)
"""
```
