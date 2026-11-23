---
name: miro-api-1-rate-limiting
description: 'Sub-skill of miro-api: 1. Rate Limiting (+3).'
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
    """Decorator for handling Miro rate limits"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) or "rate" in str(e).lower():
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limited, waiting {delay}s...")
                        time.sleep(delay)
                    else:
                        raise
            raise Exception("Max retries exceeded")
        return wrapper
    return decorator

@rate_limit_handler(max_retries=3)
def safe_create_sticky(board_id, content, x, y):
    return miro.sticky_notes.create(
        board_id=board_id,
        data={"content": content},
        position={"x": x, "y": y, "origin": "center"},
    )
```


## 2. Batch Operations


```python
# Batch creation for better performance
def batch_create_stickies(board_id: str, items: list, batch_size: int = 10):
    """Create stickies in batches to avoid rate limits"""
    created = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        for item in batch:
            sticky = miro.sticky_notes.create(
                board_id=board_id,
                data={"content": item["content"]},
                style={"fillColor": item.get("color", "yellow")},
                position={"x": item["x"], "y": item["y"], "origin": "center"},
            )
            created.append(sticky)

        # Small delay between batches
        if i + batch_size < len(items):
            time.sleep(0.5)

    return created
```


## 3. Error Handling


```python
# Comprehensive error handling
from miro_api.exceptions import MiroApiException

def safe_api_call(func, *args, **kwargs):
    """Wrapper for safe API calls"""
    try:
        return func(*args, **kwargs)
    except MiroApiException as e:
        if e.status_code == 404:
            print(f"Resource not found: {e}")
            return None
        elif e.status_code == 401:
            print("Authentication failed - check token")
            raise
        elif e.status_code == 403:
            print("Permission denied - check scopes")
            raise
        elif e.status_code == 429:
            print("Rate limited - implement backoff")
            time.sleep(60)
            return func(*args, **kwargs)
        else:
            raise
```


## 4. Position Calculations


```python
# Helper functions for positioning
def calculate_grid_position(index: int, columns: int, spacing: float = 250):
    """Calculate x, y for grid layout"""
    row = index // columns
    col = index % columns
    return {
        "x": col * spacing,
        "y": row * spacing,
    }

def calculate_circle_position(index: int, total: int, radius: float = 300, center_x: float = 0, center_y: float = 0):
    """Calculate x, y for circular layout"""
    import math
    angle = (2 * math.pi * index) / total
    return {
        "x": center_x + radius * math.cos(angle),
        "y": center_y + radius * math.sin(angle),
    }
```
