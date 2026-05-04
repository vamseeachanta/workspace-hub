---
name: mcp-builder-pagination
description: 'Sub-skill of mcp-builder: Pagination (+2).'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# Pagination (+2)

## Pagination


```typescript
async function listAllItems(apiClient: Client): Promise<Item[]> {
  const items: Item[] = [];
  let cursor: string | undefined;

  do {
    const response = await apiClient.list({ cursor, limit: 100 });
    items.push(...response.items);
    cursor = response.nextCursor;
  } while (cursor);

  return items;
}
```

## Rate Limiting


```typescript
import Bottleneck from "bottleneck";

const limiter = new Bottleneck({
  maxConcurrent: 1,
  minTime: 100  // 10 requests per second
});

const rateLimitedFetch = limiter.wrap(fetch);
```

## Authentication


```typescript
const API_KEY = process.env.MY_API_KEY;

if (!API_KEY) {
  throw new Error(
    "MY_API_KEY environment variable is required. " +
    "Get your API key from https://example.com/settings"
  );
}
```
