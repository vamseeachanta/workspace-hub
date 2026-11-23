---
name: trello-api-common-issues
description: 'Sub-skill of trello-api: Common Issues.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: 401 Unauthorized**
```bash
# Verify credentials
curl -s "https://api.trello.com/1/members/me?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"

# Regenerate token if needed:
# https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&key=YOUR_API_KEY
```

**Issue: 429 Rate Limited**
```python
# Implement exponential backoff
import time

def retry_with_backoff(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e):
                wait = 2 ** i
                print(f"Rate limited, waiting {wait}s")
                time.sleep(wait)
            else:
                raise
```

**Issue: Card not found**
```python
# Cards may be archived - search with filter
cards = board.get_cards(card_filter="all")  # Includes archived
```

**Issue: Webhook not receiving events**
```bash
# Check webhook status
curl -s "https://api.trello.com/1/tokens/$TRELLO_TOKEN/webhooks?key=$TRELLO_API_KEY" | jq

# Ensure callback URL is HTTPS and publicly accessible
```
