---
name: calendly-api-1-rate-limiting
description: 'Sub-skill of calendly-api: 1. Rate Limiting (+3).'
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
    """Decorator for handling Calendly rate limits"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e):
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limited, waiting {delay}s...")
                        time.sleep(delay)
                    else:
                        raise
            raise Exception("Max retries exceeded")
        return wrapper
    return decorator
```


## 2. Token Management


```python
# Secure token management
import os
from functools import lru_cache

@lru_cache()
def get_calendly_client():
    """Get cached Calendly client with secure token"""
    token = os.environ.get("CALENDLY_API_KEY")
    if not token:
        raise ValueError("CALENDLY_API_KEY not set")
    return CalendlyClient(api_key=token)

# Never log tokens
def redact_token(text: str) -> str:
    token = os.environ.get("CALENDLY_API_KEY", "")
    if token and token in text:
        return text.replace(token, "[REDACTED]")
    return text
```


## 3. Webhook Security


```python
# Webhook signature verification
def verify_and_process_webhook(request):
    """Verify webhook signature before processing"""
    signature = request.headers.get("Calendly-Webhook-Signature")

    if not signature:
        return {"error": "Missing signature"}, 401

    signing_key = os.environ.get("CALENDLY_WEBHOOK_SECRET")
    if not verify_webhook_signature(request.data, signature, signing_key):
        return {"error": "Invalid signature"}, 401

    # Process webhook
    return process_webhook(request.json)
```


## 4. Error Handling


```python
# Comprehensive error handling
class CalendlyError(Exception):
    """Base Calendly API error"""
    pass

class RateLimitError(CalendlyError):
    """Rate limit exceeded"""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after}s")

class NotFoundError(CalendlyError):
    """Resource not found"""
    pass

def handle_api_error(response):
    """Handle API error responses"""
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        raise RateLimitError(retry_after)
    elif response.status_code == 404:
        raise NotFoundError(response.json().get("message"))
    else:
        response.raise_for_status()
```
