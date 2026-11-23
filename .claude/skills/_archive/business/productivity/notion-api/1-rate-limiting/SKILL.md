---
name: notion-api-1-rate-limiting
description: 'Sub-skill of notion-api: 1. Rate Limiting (+3).'
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

def rate_limit(calls_per_second=3):
    """Decorator to rate limit API calls"""
    min_interval = 1.0 / calls_per_second
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

# Usage
@rate_limit(calls_per_second=3)
def api_call(func, *args, **kwargs):
    return func(*args, **kwargs)
```


## 2. Error Handling


```python
from notion_client import APIResponseError

def safe_notion_call(func, *args, max_retries=3, **kwargs):
    """Execute Notion API call with retry logic"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except APIResponseError as e:
            if e.status == 429:
                # Rate limited
                wait_time = int(e.headers.get("Retry-After", 60))
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.status >= 500:
                # Server error, retry
                time.sleep(2 ** attempt)
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

    raise Exception(f"Failed after {max_retries} retries")
```


## 3. Batch Operations


```python
def batch_create_pages(database_id, pages_data, batch_size=10):
    """Create pages in batches to avoid rate limits"""
    results = []
    for i in range(0, len(pages_data), batch_size):
        batch = pages_data[i:i + batch_size]
        for page_data in batch:
            result = notion.pages.create(
                parent={"database_id": database_id},
                properties=page_data["properties"],
                children=page_data.get("children", [])
            )
            results.append(result)
        if i + batch_size < len(pages_data):
            time.sleep(1)  # Brief pause between batches
    return results
```


## 4. Caching


```python
import json
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path.home() / ".cache" / "notion"
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
