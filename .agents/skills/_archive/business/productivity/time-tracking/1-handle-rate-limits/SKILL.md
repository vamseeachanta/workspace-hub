---
name: time-tracking-1-handle-rate-limits
description: 'Sub-skill of time-tracking: 1. Handle Rate Limits (+2).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Handle Rate Limits (+2)

## 1. Handle Rate Limits


```python
import time
from functools import wraps

def rate_limited(max_per_second=1):
    """Rate limiting decorator."""
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
```


## 2. Cache API Responses


```python
from functools import lru_cache
from datetime import datetime

@lru_cache(maxsize=100)
def get_projects_cached(workspace_id, cache_key=None):
    """Get projects with caching."""
    return toggl.get_projects(workspace_id)

# Invalidate cache daily
cache_key = datetime.now().strftime("%Y-%m-%d")
projects = get_projects_cached(workspace_id, cache_key)
```


## 3. Validate Time Entries


```python
def validate_time_entry(entry):
    """Validate time entry before creating."""
    if not entry.get("description"):
        raise ValueError("Description is required")

    duration = entry.get("duration", 0)
    if duration > 12 * 3600:  # More than 12 hours
        raise ValueError("Duration exceeds 12 hours")

    if duration < 60:  # Less than 1 minute
        raise ValueError("Duration too short")

    return True
```
