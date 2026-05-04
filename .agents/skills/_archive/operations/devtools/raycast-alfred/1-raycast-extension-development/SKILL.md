---
name: raycast-alfred-1-raycast-extension-development
description: 'Sub-skill of raycast-alfred: 1. Raycast Extension Development (+2).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Raycast Extension Development (+2)

## 1. Raycast Extension Development


```typescript
// Use proper error handling
import { showToast, Toast } from "@raycast/api";

async function safeFetch(url: string) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  } catch (error) {
    showToast({
      style: Toast.Style.Failure,
      title: "Request failed",
      message: String(error),
    });
    return null;
  }
}

// Use LocalStorage for persistence
import { LocalStorage } from "@raycast/api";

async function saveData(key: string, data: any) {
  await LocalStorage.setItem(key, JSON.stringify(data));
}

async function loadData<T>(key: string, defaultValue: T): Promise<T> {
  const json = await LocalStorage.getItem<string>(key);
  return json ? JSON.parse(json) : defaultValue;
}
```


## 2. Alfred Workflow Best Practices


```python
# Always output valid JSON for Script Filters
import json
import sys

def output_items(items):
    """Output Alfred JSON format"""
    print(json.dumps({"items": items}))

def output_error(message):
    """Output error as Alfred item"""
    output_items([{
        "title": "Error",
        "subtitle": message,
        "icon": {"path": "error.png"}
    }])

# Handle keyboard interrupt gracefully
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)
```


## 3. Performance Optimization


```typescript
// Debounce search queries
import { useState, useCallback } from "react";
import { useDebouncedValue } from "@raycast/utils";

function SearchCommand() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, 300);

  // Use debouncedQuery for API calls
}

// Cache API responses
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

async function cachedFetch(url: string) {
  const cached = cache.get(url);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const data = await fetch(url).then((r) => r.json());
  cache.set(url, { data, timestamp: Date.now() });
  return data;
}
```
