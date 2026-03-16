---
name: slack-api-5-slash-commands
description: 'Sub-skill of slack-api: 5. Slash Commands.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 5. Slash Commands

## 5. Slash Commands


```python
# commands.py
# ABOUTME: Slash command implementations
# ABOUTME: Various utility commands for team workflows

from slack_bolt import App
from datetime import datetime, timedelta
import random
import os

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/standup")
def handle_standup(ack, body, client, command):
    """Start a standup thread"""
    ack()

    channel = command['channel_id']
    user = command['user_id']

    # Create standup thread
    result = client.chat_postMessage(
        channel=channel,
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":sunrise: Daily Standup - {datetime.now().strftime('%A, %B %d')}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please share your updates in this thread:\n\n1. :white_check_mark: What did you accomplish yesterday?\n2. :calendar: What are you working on today?\n3. :construction: Any blockers?"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Started by <@{user}>"}
                ]
            }
        ],
        text="Daily Standup"
    )

    # Pin the standup
    client.pins_add(channel=channel, timestamp=result['ts'])

@app.command("/poll")
def handle_poll(ack, body, client, command):
    """Create a quick poll: /poll "Question" "Option 1" "Option 2" ..."""
    ack()

    text = command.get('text', '')

    # Parse quoted arguments
    import re
    parts = re.findall(r'"([^"]+)"', text)

    if len(parts) < 3:
        client.chat_postEphemeral(
            channel=command['channel_id'],
            user=command['user_id'],
            text='Usage: /poll "Question" "Option 1" "Option 2" "Option 3"'
        )
        return

    question = parts[0]
    options = parts[1:]

    # Create poll blocks
    option_blocks = []
    emojis = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']

    for i, option in enumerate(options[:9]):
        option_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emojis[i]} {option}"
            }
        })

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":bar_chart: Poll", "emoji": True}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{question}*"}
        },
        {"type": "divider"},
        *option_blocks,
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"Poll by <@{command['user_id']}> | React to vote!"}
            ]
        }
    ]

    result = client.chat_postMessage(
        channel=command['channel_id'],
        blocks=blocks,
        text=f"Poll: {question}"
    )

    # Add reaction options
    for i in range(len(options[:9])):
        emoji_names = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        client.reactions_add(
            channel=command['channel_id'],
            timestamp=result['ts'],
            name=emoji_names[i]
        )

@app.command("/remind-team")
def handle_team_reminder(ack, body, client, command):
    """Set a team reminder: /remind-team 15m Check deployment status"""
    ack()

    text = command.get('text', '').strip()
    parts = text.split(' ', 1)

    if len(parts) < 2:
        client.chat_postEphemeral(
            channel=command['channel_id'],
            user=command['user_id'],
            text='Usage: /remind-team 15m Your reminder message'
        )
        return

    time_str = parts[0]
    message = parts[1]

    # Parse time
    time_map = {'s': 1, 'm': 60, 'h': 3600}
    unit = time_str[-1]

    if unit not in time_map:
        client.chat_postEphemeral(
            channel=command['channel_id'],
            user=command['user_id'],
            text='Time format: 15s, 15m, or 2h'
        )
        return

    try:
        amount = int(time_str[:-1])
        seconds = amount * time_map[unit]
    except ValueError:
        client.chat_postEphemeral(
            channel=command['channel_id'],
            user=command['user_id'],
            text='Invalid time format'
        )
        return

    # Schedule message
    post_at = int(datetime.now().timestamp()) + seconds

    client.chat_scheduleMessage(
        channel=command['channel_id'],
        post_at=post_at,
        text=f":bell: *Reminder:* {message}\n\n_Set by <@{command['user_id']}>_"
    )

    client.chat_postEphemeral(
        channel=command['channel_id'],
        user=command['user_id'],
        text=f"Reminder scheduled for {time_str} from now!"
    )

@app.command("/random-pick")
def handle_random_pick(ack, body, client, command):

*Content truncated — see parent skill for full reference.*
