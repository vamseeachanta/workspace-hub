---
name: bsee-sodir-extraction-1-rate-limiting
description: 'Sub-skill of bsee-sodir-extraction: 1. Rate Limiting (+2).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Rate Limiting (+2)

## 1. Rate Limiting


```python
import time
from functools import wraps

def rate_limit(calls_per_minute: int = 30):
    """Decorator to rate limit API calls."""
    min_interval = 60.0 / calls_per_minute
    last_call = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_call[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_minute=30)
def fetch_with_rate_limit(url: str) -> requests.Response:
    return requests.get(url)
```


## 2. Caching


```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def cached_fetch(url: str, cache_hours: int = 24) -> pd.DataFrame:
    """Fetch with caching."""
    cache_file = Path(f".cache/{hash(url)}.parquet")

    if cache_file.exists():
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - mtime < timedelta(hours=cache_hours):
            return pd.read_parquet(cache_file)

    # Fetch fresh data
    response = requests.get(url)
    df = pd.DataFrame(response.json())

    cache_file.parent.mkdir(exist_ok=True)
    df.to_parquet(cache_file)

    return df
```


## 3. Error Handling


```python
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def robust_fetch(url: str) -> requests.Response:
    """Fetch with automatic retry on failure."""
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Fetch failed for {url}: {e}")
        raise
```
