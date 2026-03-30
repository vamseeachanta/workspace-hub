---
name: trello-api-1-use-batch-operations
description: 'Sub-skill of trello-api: 1. Use Batch Operations (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Use Batch Operations (+3)

## 1. Use Batch Operations


```python
# GOOD: Batch operations when possible
import requests

def batch_create_cards(list_id, cards):
    """Create multiple cards efficiently."""
    for card in cards:
        requests.post(
            "https://api.trello.com/1/cards",
            data={
                "key": API_KEY,
                "token": TOKEN,
                "idList": list_id,
                **card
            }
        )
        # Small delay to avoid rate limits
        time.sleep(0.1)

# AVOID: Individual requests without batching consideration
```


## 2. Handle Rate Limits


```python
import time
from functools import wraps

def rate_limit(max_per_second=10):
    """Rate limit decorator."""
    min_interval = 1.0 / max_per_second
    last_call = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_call[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(max_per_second=10)
def api_call(endpoint, **kwargs):
    return requests.get(endpoint, params=kwargs)
```


## 3. Cache Board Data


```python
from functools import lru_cache
from datetime import datetime, timedelta

class TrelloCache:
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self.cache = {}

    def get_board(self, client, board_id):
        key = f"board_{board_id}"
        now = datetime.now()

        if key in self.cache:
            data, timestamp = self.cache[key]
            if now - timestamp < timedelta(seconds=self.ttl):
                return data

        board = client.get_board(board_id)
        self.cache[key] = (board, now)
        return board
```


## 4. Error Handling


```python
import requests
from requests.exceptions import RequestException

def safe_trello_request(method, url, **kwargs):
    """Make Trello API request with error handling."""
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limited - wait and retry
            time.sleep(10)
            return safe_trello_request(method, url, **kwargs)
        elif e.response.status_code == 401:
            raise Exception("Invalid API credentials")
        else:
            raise
    except RequestException as e:
        raise Exception(f"Network error: {e}")
```
