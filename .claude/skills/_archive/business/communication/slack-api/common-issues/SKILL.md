---
name: slack-api-common-issues
description: 'Sub-skill of slack-api: Common Issues (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: Bot not responding to messages**
```python
# Verify bot has correct scopes
# Check Event Subscriptions are enabled
# Ensure Request URL is verified

# Debug with logging
import logging
logging.basicConfig(level=logging.DEBUG)

@app.event("message")
def debug_messages(body, logger):
    logger.info(f"Received message event: {body}")
```

**Issue: Interactive components not working**
```python
# Ensure Interactive Components URL is set
# Check action_id matches handler

@app.action("button_click")  # Must match action_id in block
def handle_click(ack, body, logger):
    ack()
    logger.info(f"Button clicked: {body}")
```

**Issue: Socket Mode connection drops**
```python
# Increase connection timeout
from slack_bolt.adapter.socket_mode import SocketModeHandler

handler = SocketModeHandler(
    app,
    app_token,
    ping_interval=30  # Send ping every 30 seconds
)
```

**Issue: Message not appearing in channel**
```python
# Check channel ID format
# Verify bot is in channel

def ensure_in_channel(client, channel):
    try:
        client.conversations_info(channel=channel)
    except:
        client.conversations_join(channel=channel)
```


## Debug Commands


```bash
# Test webhook
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}' \
  $SLACK_WEBHOOK_URL

# Test bot token
curl -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  https://slack.com/api/auth.test

# List channels
curl -X GET \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.list?limit=10"
```
