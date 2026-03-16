---
name: slack-api-1-basic-slack-bot-with-bolt
description: 'Sub-skill of slack-api: 1. Basic Slack Bot with Bolt.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Basic Slack Bot with Bolt

## 1. Basic Slack Bot with Bolt


```python
# app.py
# ABOUTME: Basic Slack bot using Bolt framework
# ABOUTME: Handles messages, mentions, and slash commands

import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

# Initialize app with bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Listen for messages containing "hello"
@app.message("hello")
def message_hello(message, say):
    """Respond to messages containing 'hello'"""
    user = message['user']
    say(f"Hey there <@{user}>!")

# Listen for app mentions
@app.event("app_mention")
def handle_app_mention(event, say, client):
    """Respond when bot is mentioned"""
    user = event['user']
    channel = event['channel']
    text = event['text']

    # Get user info
    user_info = client.users_info(user=user)
    user_name = user_info['user']['real_name']

    say(f"Hi {user_name}! You mentioned me with: {text}")

# Handle message events
@app.event("message")
def handle_message_events(body, logger):
    """Log all message events"""
    logger.info(f"Message event: {body}")

# Slash command handler
@app.command("/greet")
def handle_greet_command(ack, say, command):
    """Handle /greet slash command"""
    ack()  # Acknowledge command within 3 seconds

    user = command['user_id']
    text = command.get('text', 'everyone')

    say(f"<@{user}> sends greetings to {text}!")

# Error handler
@app.error
def custom_error_handler(error, body, logger):
    """Handle errors gracefully"""
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")

# Run with Socket Mode (no public URL needed)
if __name__ == "__main__":
    handler = SocketModeHandler(
        app,
        os.environ.get("SLACK_APP_TOKEN")
    )
    print("Bot is running...")
    handler.start()
```
