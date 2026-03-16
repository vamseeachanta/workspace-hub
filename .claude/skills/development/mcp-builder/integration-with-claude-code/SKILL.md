---
name: mcp-builder-integration-with-claude-code
description: 'Sub-skill of mcp-builder: Integration with Claude Code.'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# Integration with Claude Code

## Integration with Claude Code


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
