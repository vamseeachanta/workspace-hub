---
name: teams-api-4-bot-framework-integration
description: 'Sub-skill of teams-api: 4. Bot Framework Integration.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 4. Bot Framework Integration

## 4. Bot Framework Integration


```python
# bot.py
# ABOUTME: Teams bot using Bot Framework SDK
# ABOUTME: Handles messages, cards, and proactive messaging

from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    CardFactory,
    MessageFactory
)
from botbuilder.schema import (
    Activity,
    ActivityTypes,
    ChannelAccount,
    Attachment
)
import json

class TeamsBot(ActivityHandler):
    """Microsoft Teams bot handler"""

    def __init__(self, conversation_references: dict = None):
        self.conversation_references = conversation_references or {}

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages"""

        # Store conversation reference for proactive messaging
        self._add_conversation_reference(turn_context.activity)

        text = turn_context.activity.text.lower().strip()
        user_name = turn_context.activity.from_property.name

        if text == "help":
            await self._send_help_card(turn_context)
        elif text == "status":
            await self._send_status_card(turn_context)
        elif text.startswith("deploy"):
            await self._handle_deploy_command(turn_context, text)
        else:
            await turn_context.send_activity(
                f"Hi {user_name}! I received: '{text}'. Type 'help' for commands."
            )

    async def on_members_added_activity(
        self,
        members_added: list,
        turn_context: TurnContext
    ):
        """Handle new members added to conversation"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Welcome to the team, {member.name}! "
                    "Type 'help' to see available commands."
                )

    async def on_adaptive_card_invoke(
        self,
        turn_context: TurnContext,
        invoke_value: dict
    ):
        """Handle Adaptive Card action invocations"""

        action = invoke_value.get("action")
        data = invoke_value

        if action == "approve":
            return await self._handle_approval(turn_context, data, approved=True)
        elif action == "reject":
            return await self._handle_approval(turn_context, data, approved=False)
        elif action == "vote":
            return await self._handle_vote(turn_context, data)

        return {"status": 200}

    async def _send_help_card(self, turn_context: TurnContext):
        """Send help card"""

        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "Bot Commands",
                    "size": "large",
                    "weight": "bolder"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "help", "value": "Show this help message"},
                        {"title": "status", "value": "Show system status"},
                        {"title": "deploy [env]", "value": "Trigger deployment"},
                        {"title": "poll [question]", "value": "Create a poll"}
                    ]
                }
            ]
        }

        attachment = Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card
        )

        await turn_context.send_activity(
            MessageFactory.attachment(attachment)
        )

    async def _send_status_card(self, turn_context: TurnContext):
        """Send status card"""

        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "System Status",
                    "size": "large",
                    "weight": "bolder"
                },
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {"type": "TextBlock", "text": "API", "weight": "bolder"},
                                {"type": "TextBlock", "text": "Healthy", "color": "good"}
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {"type": "TextBlock", "text": "Database", "weight": "bolder"},
                                {"type": "TextBlock", "text": "Healthy", "color": "good"}
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {"type": "TextBlock", "text": "Cache", "weight": "bolder"},
                                {"type": "TextBlock", "text": "Warning", "color": "warning"}
                            ]
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "View Dashboard",
                    "url": "https://status.example.com"
                }
            ]
        }

        attachment = Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card
        )

        await turn_context.send_activity(
            MessageFactory.attachment(attachment)
        )

    async def _handle_deploy_command(
        self,
        turn_context: TurnContext,
        text: str
    ):
        """Handle deploy command"""

        parts = text.split()
        environment = parts[1] if len(parts) > 1 else "staging"


*Content truncated — see parent skill for full reference.*
