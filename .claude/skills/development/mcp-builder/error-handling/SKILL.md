---
name: mcp-builder-error-handling
description: 'Sub-skill of mcp-builder: Error Handling.'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


| Error | Cause | Solution |
|-------|-------|----------|
| `ECONNREFUSED` | Server not running | Start the MCP server process |
| `Tool not found` | Incorrect tool name | Check ListToolsRequestSchema handler |
| `Invalid arguments` | Schema mismatch | Validate against inputSchema |
| `Authentication failed` | Missing/invalid API key | Set environment variable correctly |
| `Timeout` | Slow response | Increase MCP_TIMEOUT or optimize handler |
### Error Template


```typescript
try {
  const result = await operation();
  return { content: [{ type: "text", text: JSON.stringify(result) }] };
} catch (error) {
  throw new Error(
    `Operation failed: ${error.message}. ` +
    `Please check your configuration and try again.`
  );
}
```
