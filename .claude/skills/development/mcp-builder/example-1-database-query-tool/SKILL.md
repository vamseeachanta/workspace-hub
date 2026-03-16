---
name: mcp-builder-example-1-database-query-tool
description: 'Sub-skill of mcp-builder: Example 1: Database Query Tool (+1).'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Database Query Tool (+1)

## Example 1: Database Query Tool


```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "query_database") {
    const { sql, params } = request.params.arguments;
    const result = await db.query(sql, params);
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
});
```


## Example 2: API Integration


```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "fetch_weather") {
    const { city } = request.params.arguments;
    const response = await fetch(`https://api.weather.com/v1/${city}`);
    const data = await response.json();
    return { content: [{ type: "text", text: `Temperature: ${data.temp}F` }] };
  }
});
```
