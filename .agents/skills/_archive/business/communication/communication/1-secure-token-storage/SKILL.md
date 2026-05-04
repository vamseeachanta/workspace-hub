---
name: communication-1-secure-token-storage
description: 'Sub-skill of communication: 1. Secure Token Storage (+4).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Secure Token Storage (+4)

## 1. Secure Token Storage

```bash
# Use environment variables or secret managers
export SLACK_BOT_TOKEN=$(vault kv get -field=token secret/slack)

# Rotate tokens regularly
rotate_token() {
    local new_token=$(generate_new_token)
    vault kv put secret/slack token="$new_token"
}
```


## 2. Message Formatting

```bash
# Escape special characters for Slack
escape_slack() {
    local text="$1"
    text="${text//&/&amp;}"
    text="${text//</&lt;}"
    text="${text//>/&gt;}"
    echo "$text"
}

# Format mentions
format_mention() {
    local user_id="$1"
    echo "<@$user_id>"
}

# Format channel link
format_channel() {
    local channel_id="$1"
    echo "<#$channel_id>"
}
```


## 3. Idempotent Operations

```bash
# Prevent duplicate messages
SENT_MESSAGES_FILE="/tmp/sent_messages.txt"

send_once() {
    local message_hash=$(echo "$1" | md5sum | cut -d' ' -f1)

    if grep -q "$message_hash" "$SENT_MESSAGES_FILE" 2>/dev/null; then
        echo "Message already sent" >&2
        return 0
    fi

    if send_message "$1"; then
        echo "$message_hash" >> "$SENT_MESSAGES_FILE"
    fi
}
```


## 4. Webhook Verification

```bash
# Verify Slack signature
verify_slack_signature() {
    local timestamp="$1"
    local body="$2"
    local signature="$3"

    local base="v0:$timestamp:$body"
    local computed=$(echo -n "$base" | openssl dgst -sha256 -hmac "$SLACK_SIGNING_SECRET" | sed 's/.*= //')

    [ "v0=$computed" = "$signature" ]
}
```


## 5. Graceful Degradation

```bash
# Fallback when primary channel fails
notify() {
    local message="$1"

    if ! send_slack_message "$message"; then
        echo "Slack failed, trying Teams..." >&2
        if ! send_teams_message "$message"; then
            echo "Teams failed, sending email..." >&2
            send_email "$message"
        fi
    fi
}
```
