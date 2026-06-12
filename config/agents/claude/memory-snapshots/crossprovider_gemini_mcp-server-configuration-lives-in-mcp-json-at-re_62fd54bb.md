---
name: crossprovider gemini mcp-server-configuration-lives-in-mcp-json-at-re
description: MCP server configuration lives in .mcp.json at repo root, not settings.json
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [mcp, configuration, file-location]
---

Plans that target MCP server removal or updates in `settings.json` variants will miss the actual configuration in `.mcp.json`. This is the canonical location for MCP server setup and must be checked first.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
