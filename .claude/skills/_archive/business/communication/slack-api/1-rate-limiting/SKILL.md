---
name: slack-api-1-rate-limiting
description: 'Sub-skill of slack-api: 1. Rate Limiting (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Rate Limiting (+3)

## 1. Rate Limiting


```python
# Rate limit handling
import time
from functools import wraps

def rate_limit_handler(max_retries=3, base_delay=1):
    """Decorator for handling Slack rate limits"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "rate_limited" in str(e):
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                    else:
                        raise
            raise Exception("Max retries exceeded")
        return wrapper
    return decorator

@rate_limit_handler(max_retries=3)
def send_message(client, channel, text):
    return client.chat_postMessage(channel=channel, text=text)
```


## 2. Error Handling


```python
# Comprehensive error handling
from slack_sdk.errors import SlackApiError

def safe_send_message(client, channel, text, blocks=None):
    """Send message with error handling"""
    try:
        result = client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks
        )
        return result
    except SlackApiError as e:
        error_code = e.response.get("error", "unknown_error")

        if error_code == "channel_not_found":
            # Handle missing channel
            raise ValueError(f"Channel {channel} not found")
        elif error_code == "not_in_channel":
            # Try to join channel first
            client.conversations_join(channel=channel)
            return client.chat_postMessage(channel=channel, text=text, blocks=blocks)
        elif error_code == "ratelimited":
            # Wait and retry
            retry_after = int(e.response.headers.get("Retry-After", 1))
            time.sleep(retry_after)
            return safe_send_message(client, channel, text, blocks)
        else:
            raise
```


## 3. Message Formatting


```python
# Safe message formatting
def escape_text(text: str) -> str:
    """Escape special characters for Slack"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def format_user_mention(user_id: str) -> str:
    """Format user mention"""
    return f"<@{user_id}>"

def format_channel_link(channel_id: str) -> str:
    """Format channel link"""
    return f"<#{channel_id}>"

def format_url(url: str, text: str = None) -> str:
    """Format URL with optional text"""
    if text:
        return f"<{url}|{escape_text(text)}>"
    return f"<{url}>"

def format_code_block(code: str, language: str = "") -> str:
    """Format code block"""
    return f"```{language}\n{code}\n```"
```


## 4. Token Security


```python
# Secure token management
import os
from functools import lru_cache

@lru_cache()
def get_slack_client():
    """Get cached Slack client with secure token"""
    from slack_sdk import WebClient

    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN not set")

    if not token.startswith("xoxb-"):
        raise ValueError("Invalid bot token format")

    return WebClient(token=token)

# Never log tokens
import logging
class TokenFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            record.msg = str(record.msg).replace(
                os.environ.get("SLACK_BOT_TOKEN", ""), "[REDACTED]"
            )
        return True
```
