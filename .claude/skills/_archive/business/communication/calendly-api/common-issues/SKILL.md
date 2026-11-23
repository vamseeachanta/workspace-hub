---
name: calendly-api-common-issues
description: 'Sub-skill of calendly-api: Common Issues (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: 401 Unauthorized**
```python
# Verify token is valid
def verify_token(token: str) -> bool:
    response = requests.get(
        "https://api.calendly.com/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.status_code == 200
```

**Issue: No events returned**
```python
# Check time range format
from datetime import datetime

def format_time_for_api(dt: datetime) -> str:
    """Format datetime for Calendly API (ISO 8601 with Z)"""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

# Ensure UTC timezone
start = datetime.utcnow()
formatted = format_time_for_api(start)
```

**Issue: Webhook not receiving events**
```python
# Verify webhook subscription
def check_webhook_status(webhook_uri: str):
    webhook = get_webhook_subscription(webhook_uri)
    print(f"Status: {webhook.get('state')}")
    print(f"Events: {webhook.get('events')}")
    print(f"URL: {webhook.get('callback_url')}")

    # Verify URL is accessible
    import requests
    try:
        response = requests.post(webhook["callback_url"], json={"test": True})
        print(f"URL accessible: {response.status_code < 500}")
    except Exception as e:
        print(f"URL not accessible: {e}")
```


## Debug Commands


```bash
# Test API authentication
curl -X GET "https://api.calendly.com/users/me" \
  -H "Authorization: Bearer $CALENDLY_API_KEY"

# List event types
curl -X GET "https://api.calendly.com/event_types?user=$(curl -s -X GET https://api.calendly.com/users/me -H "Authorization: Bearer $CALENDLY_API_KEY" | jq -r '.resource.uri')" \
  -H "Authorization: Bearer $CALENDLY_API_KEY"

# List webhooks
curl -X GET "https://api.calendly.com/webhook_subscriptions?organization=$(curl -s -X GET https://api.calendly.com/users/me -H "Authorization: Bearer $CALENDLY_API_KEY" | jq -r '.resource.current_organization')" \
  -H "Authorization: Bearer $CALENDLY_API_KEY"
```
