---
name: communication-slack-message-posting
description: 'Sub-skill of communication: Slack Message Posting (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Slack Message Posting (+3)

## Slack Message Posting

```bash
# See slack-api for complete patterns

# Simple webhook message
send_slack_webhook() {
    local webhook_url="$SLACK_WEBHOOK_URL"
    local message="$1"

    curl -s -X POST "$webhook_url" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$message\"}"
}

# Rich Block Kit message
send_slack_blocks() {
    local channel="$1"
    local blocks="$2"

    curl -s -X POST "https://slack.com/api/chat.postMessage" \
        -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"channel\": \"$channel\",
            \"blocks\": $blocks
        }"
}

# Example Block Kit payload
blocks='[
    {
        "type": "header",
        "text": {"type": "plain_text", "text": "Deployment Complete"}
    },
    {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": "*Environment:*\nProduction"},
            {"type": "mrkdwn", "text": "*Version:*\nv2.1.0"}
        ]
    },
    {
        "type": "actions",
        "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "View Logs"}, "url": "https://logs.example.com"}
        ]
    }
]'

send_slack_blocks "#deployments" "$blocks"
```


## Teams Message via Graph API

```bash
# See teams-api for complete patterns

# Send channel message
send_teams_message() {
    local team_id="$1"
    local channel_id="$2"
    local message="$3"

    curl -s -X POST "https://graph.microsoft.com/v1.0/teams/$team_id/channels/$channel_id/messages" \
        -H "Authorization: Bearer $TEAMS_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"body\": {
                \"contentType\": \"html\",
                \"content\": \"$message\"
            }
        }"
}

# Send adaptive card
send_teams_card() {
    local webhook_url="$1"
    local card="$2"

    curl -s -X POST "$webhook_url" \
        -H "Content-Type: application/json" \
        -d "{
            \"type\": \"message\",
            \"attachments\": [{
                \"contentType\": \"application/vnd.microsoft.card.adaptive\",
                \"content\": $card
            }]
        }"
}
```


## Miro Board Operations

```bash
# See miro-api for complete patterns

# Create sticky note
create_sticky() {
    local board_id="$1"
    local content="$2"
    local x="${3:-0}"
    local y="${4:-0}"

    curl -s -X POST "https://api.miro.com/v2/boards/$board_id/sticky_notes" \
        -H "Authorization: Bearer $MIRO_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"data\": {\"content\": \"$content\"},
            \"position\": {\"x\": $x, \"y\": $y}
        }"
}

# Create frame
create_frame() {
    local board_id="$1"
    local title="$2"

    curl -s -X POST "https://api.miro.com/v2/boards/$board_id/frames" \
        -H "Authorization: Bearer $MIRO_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"data\": {\"title\": \"$title\"},
            \"geometry\": {\"width\": 800, \"height\": 600}
        }"
}
```


## Calendly Event Management

```bash
# See calendly-api for complete patterns

# List scheduled events
list_events() {
    local user_uri="$1"
    local min_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    curl -s "https://api.calendly.com/scheduled_events?user=$user_uri&min_start_time=$min_time" \
        -H "Authorization: Bearer $CALENDLY_API_KEY"
}

# Get event details
get_event() {
    local event_uuid="$1"

    curl -s "https://api.calendly.com/scheduled_events/$event_uuid" \
        -H "Authorization: Bearer $CALENDLY_API_KEY"
}

# Create webhook subscription
create_webhook() {
    local organization="$1"
    local callback_url="$2"

    curl -s -X POST "https://api.calendly.com/webhook_subscriptions" \
        -H "Authorization: Bearer $CALENDLY_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"url\": \"$callback_url\",
            \"events\": [\"invitee.created\", \"invitee.canceled\"],
            \"organization\": \"$organization\",
            \"scope\": \"organization\"
        }"
}
```
