---
name: mcp-builder
description: Guide for building high-quality Model Context Protocol (MCP) servers that allow LLMs to interact with external services. Use when creating new MCP integrations, tools, or servers for Claude or other AI systems.
version: 1.1.0
last_updated: 2025-12-30
---

# MCP Builder Skill

## Overview

This skill teaches how to build high-quality MCP servers that allow large language models to interact with external services through well-designed tools.

## Four-Phase Development Process

### Phase 1: Deep Research and Planning

**Study MCP Design Principles:**
- Balance "API coverage vs. workflow tools"
- Review MCP protocol at modelcontextprotocol.io
- Learn framework specifics (TypeScript recommended)
- Analyze target API endpoints

**Key Questions:**
1. What actions does the user want to perform?
2. What API endpoints are available?
3. Which operations are read-only vs destructive?
4. How should errors be handled?

### Phase 2: Implementation

**Project Setup (TypeScript):**
```bash
mkdir my-mcp-server
cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node
```

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src/**/*"]
}
```

**Basic Server Structure:**
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "my-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "my_tool",
      description: "Description of what this tool does",
      inputSchema: {
        type: "object",
        properties: {
          param1: { type: "string", description: "First parameter" },
          param2: { type: "number", description: "Second parameter" }
        },
        required: ["param1"]
      }
    }
  ]
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "my_tool") {
    // Tool implementation
    return {
      content: [{ type: "text", text: "Result" }]
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Phase 3: Review and Test

**Code Quality Checklist:**
- [ ] No code duplication
- [ ] Full type coverage
- [ ] Proper error handling
- [ ] Input validation
- [ ] Rate limiting (if needed)

**Testing with MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

### Phase 4: Create Evaluations

Generate 10 complex, realistic test questions:
- Independent (no dependencies between questions)
- Read-only (don't modify external state)
- Verifiable (clear expected answers)

## Key Recommendations

### Language Choice
**TypeScript preferred** for:
- High-quality SDK support
- Good compatibility
- Strong typing

### Transport Selection
- **Streamable HTTP**: Remote servers
- **stdio**: Local servers

### Tool Naming
Use consistent, action-oriented prefixes:
```
github_create_issue
github_list_repos
slack_send_message
slack_list_channels
```

### Error Messages
Provide actionable messages with specific next steps:
```typescript
throw new Error(
  `Failed to fetch repository: ${error.message}. ` +
  `Check that the repository exists and you have access.`
);
```

### Tool Annotations
```typescript
{
  name: "delete_file",
  description: "Permanently delete a file",
  inputSchema: { /* ... */ },
  annotations: {
    destructiveHint: true,
    readOnlyHint: false,
    confirmationHint: "Are you sure you want to delete this file?"
  }
}
```

## Advanced Patterns

### Pagination
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

### Rate Limiting
```typescript
import Bottleneck from "bottleneck";

const limiter = new Bottleneck({
  maxConcurrent: 1,
  minTime: 100  // 10 requests per second
});

const rateLimitedFetch = limiter.wrap(fetch);
```

### Authentication
```typescript
const API_KEY = process.env.MY_API_KEY;

if (!API_KEY) {
  throw new Error(
    "MY_API_KEY environment variable is required. " +
    "Get your API key from https://example.com/settings"
  );
}
```

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

## Project Configuration (New in 2025)

### .mcp.json for Team Sharing

Commit MCP server configs to your repository:

```json
// .mcp.json (project root)
{
  "mcpServers": {
    "project-db": {
      "command": "node",
      "args": ["./tools/mcp-server/dist/index.js"],
      "env": {
        "DB_PATH": "./data/project.db"
      }
    }
  }
}
```

**Scope changes (2025):**
- `project` scope → Now called `local` (per-project)
- `global` scope → Now called `user` (user-wide)
- **New**: Checked-in `.mcp.json` files for team sharing

### Permission Wildcards

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

### Timeout Configuration

```bash
# Set MCP server startup timeout (default: 30s)
export MCP_TIMEOUT=60000  # 60 seconds

# Debug mode for troubleshooting
claude --mcp-debug
```

## Security Best Practices

1. **Use trusted servers** - Only from official/verified sources
2. **Least privilege** - Grant minimal required permissions
3. **Audit logs** - Maintain comprehensive access logs
4. **Environment isolation** - Use containers for high-risk automation
5. **No hardcoded secrets** - Always use environment variables

## Resources

- MCP Documentation: https://modelcontextprotocol.io
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- MCP Inspector: https://github.com/modelcontextprotocol/inspector
- Top MCP Servers: https://mcpcat.io/guides/best-mcp-servers-for-claude-code/

---

## Version History

- **1.1.0** (2025-12-30): Added .mcp.json project config, permission wildcards, MCP_TIMEOUT, security best practices
- **1.0.0** (2025-10-15): Initial release with four-phase development process
