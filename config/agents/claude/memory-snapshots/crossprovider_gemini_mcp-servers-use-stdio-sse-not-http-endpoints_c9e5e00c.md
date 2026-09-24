---
name: crossprovider gemini mcp-servers-use-stdio-sse-not-http-endpoints
description: MCP servers use stdio/SSE, not HTTP endpoints
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [mcp, configuration, tooling]
---

MCP diagnostics and configuration must account for stdio and SSE transports, not curl-based HTTP endpoints. MCP configuration lives in root `.mcp.json` and `claude_desktop_config.json`, not settings.json variants. Searching only settings.json will miss active MCP wiring.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
