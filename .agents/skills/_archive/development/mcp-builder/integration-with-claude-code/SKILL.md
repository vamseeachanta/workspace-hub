---
name: mcp-builder-integration-with-Codex
description: 'Sub-skill of mcp-builder: Integration with Codex.'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# Integration with Codex

## Integration with Codex


**Add to claude_desktop_config.json:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/dist/index.js"],
      "env": {
        "MY_API_KEY": "your-api-key"
      }
    }
  }
}
```
