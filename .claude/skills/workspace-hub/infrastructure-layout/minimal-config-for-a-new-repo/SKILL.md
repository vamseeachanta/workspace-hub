---
name: infrastructure-layout-minimal-config-for-a-new-repo
description: 'Sub-skill of infrastructure-layout: Minimal `config/` for a new repo
  (+1).'
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# Minimal `config/` for a new repo (+1)

## Minimal `config/` for a new repo


```python
# src/<pkg>/infrastructure/config/settings.py
from pydantic_settings import BaseSettings

class GlobalSettings(BaseSettings):
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = ""

    class Config:
        env_prefix = "APP_"
        env_file = ".env"
```


## Minimal `persistence/` for a new repo


```python
# src/<pkg>/infrastructure/persistence/cache.py
import time
from typing import Any, Dict, Optional, Tuple

class TTLCache:
    """Simple TTL cache for in-process result reuse."""
    def __init__(self, ttl_seconds: int = 300):
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, ts = self._store[key]
            if time.time() - ts < self._ttl:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (value, time.time())
```

---
