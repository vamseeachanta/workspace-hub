---
name: todoist-api-1-rate-limiting
description: 'Sub-skill of todoist-api: 1. Rate Limiting (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Rate Limiting (+3)

## 1. Rate Limiting


```python
import time
from functools import wraps

def rate_limit(calls_per_minute=50):
    """Decorator to rate limit API calls"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_minute=50)
def api_call(func, *args, **kwargs):
    return func(*args, **kwargs)
```


## 2. Error Handling


```python
from todoist_api_python import TodoistAPI
import requests

def safe_api_call(func, *args, max_retries=3, **kwargs):
    """Execute API call with retry logic"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited
                wait_time = int(e.response.headers.get("Retry-After", 60))
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.response.status_code >= 500:
                # Server error, retry
                time.sleep(2 ** attempt)
            else:
                raise
        except requests.exceptions.ConnectionError:
            time.sleep(2 ** attempt)

    raise Exception(f"Failed after {max_retries} retries")
```


## 3. Batch Operations


```python
def batch_create_tasks(tasks, batch_size=50):
    """Create tasks in batches to avoid rate limits"""
    results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = sync_batch_add(batch)
        results.extend(batch_results)
        if i + batch_size < len(tasks):
            time.sleep(1)  # Brief pause between batches
    return results
```


## 4. Caching


```python
import json
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path.home() / ".cache" / "todoist"
CACHE_TTL = timedelta(minutes=5)

def get_cached_or_fetch(key, fetch_func, ttl=CACHE_TTL):
    """Get from cache or fetch fresh data"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{key}.json"

    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        cached_at = datetime.fromisoformat(data["cached_at"])
        if datetime.now() - cached_at < ttl:
            return data["value"]

    value = fetch_func()
    cache_data = {
        "cached_at": datetime.now().isoformat(),
        "value": value
    }
    cache_file.write_text(json.dumps(cache_data, default=str))
    return value
```
