---
name: mcp-builder-mcpjson-for-team-sharing
description: 'Sub-skill of mcp-builder: .mcp.json for Team Sharing (+2).'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# .mcp.json for Team Sharing (+2)

## .mcp.json for Team Sharing


Commit MCP server configs to your repository:

```json
// .mcp.json (project root)
{
  "mcpServers": {
    "project-db": {
      "command": "node",
      "args": ["./tools/mcp-server/dist/index.js"],
      "env": {

*See sub-skills for full details.*

## Permission Wildcards


Use wildcard syntax for server permissions:

```bash
# Allow all tools from a server
mcp__my-server__*

# In settings.json allowlist
{
  "permissions": {
    "allow": ["mcp__database__*", "mcp__github__*"]
  }
}
```

## Timeout Configuration


```bash
# Set MCP server startup timeout (default: 30s)
export MCP_TIMEOUT=60000  # 60 seconds

# Debug mode for troubleshooting
claude --mcp-debug
```
