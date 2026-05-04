---
name: teams-api-1-rate-limiting
description: 'Sub-skill of teams-api: 1. Rate Limiting (+2).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Rate Limiting (+2)

## 1. Rate Limiting


```python
# Respect Graph API rate limits
import time
from functools import wraps

def rate_limit_handler(max_retries=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e):  # Too Many Requests
                        delay = 2 ** attempt
                        await asyncio.sleep(delay)
                    else:
                        raise
            raise Exception("Max retries exceeded")
        return wrapper
    return decorator
```


## 2. Token Management


```python
# Secure token handling
from azure.identity import DefaultAzureCredential
from functools import lru_cache

@lru_cache()
def get_credential():
    """Get cached Azure credential"""
    return DefaultAzureCredential()

# Use managed identity in production
# Use environment variables for local dev
```


## 3. Card Design


```python
# Adaptive Card best practices
def create_accessible_card():
    return {
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": "Important Message",
                "size": "large",
                "weight": "bolder",
                # Always include fallback text
                "fallback": "drop"
            }
        ],
        # Provide fallback for older clients
        "fallbackText": "This card requires a newer Teams client."
    }
```
