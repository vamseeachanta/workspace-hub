---
name: mcp-builder
description: Guide for building high-quality Model Context Protocol (MCP) servers
  that allow LLMs to interact with external services. Use when creating new MCP integrations,
  tools, or servers for Claude or other AI systems.
version: 1.2.0
category: development
related_skills:
- yaml-workflow-executor
- webapp-testing
- git-worktree-workflow
capabilities: []
requires: []
see_also:
- mcp-builder-phase-1-deep-research-and-planning
- mcp-builder-language-choice
- mcp-builder-pagination
- mcp-builder-integration-with-claude-code
- mcp-builder-mcpjson-for-team-sharing
- mcp-builder-security-best-practices
tags: []
---

# Mcp Builder

## Overview

This skill teaches how to build high-quality MCP servers that allow large language models to interact with external services through well-designed tools.

## Quick Start

```bash
# Create and setup MCP server project
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node

# Create source directory
mkdir src
```

```typescript
// src/index.ts - Minimal MCP Server
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "my-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "hello_world",

*See sub-skills for full details.*

## When to Use

- Creating integrations for Claude Code with external APIs
- Building custom tooling for AI-assisted workflows
- Extending Claude's capabilities with domain-specific tools
- Automating interactions with third-party services
- Building reusable MCP servers for team sharing

## Resources

- MCP Documentation: https://modelcontextprotocol.io
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- MCP Inspector: https://github.com/modelcontextprotocol/inspector
- Top MCP Servers: https://mcpcat.io/guides/best-mcp-servers-for-claude-code/

## Related Skills

- [yaml-workflow-executor](../yaml-workflow-executor/SKILL.md) - Workflow automation
- [webapp-testing](../webapp-testing/SKILL.md) - Testing web integrations
- [git-worktree-workflow](../git-worktree-workflow/SKILL.md) - Parallel development

---

## Version History

- **1.2.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format with Quick Start, Error Handling, Metrics, Execution Checklist
- **1.1.0** (2025-12-30): Added .mcp.json project config, permission wildcards, MCP_TIMEOUT, security best practices
- **1.0.0** (2025-10-15): Initial release with four-phase development process

## Sub-Skills

- [Example 1: Database Query Tool (+1)](example-1-database-query-tool/SKILL.md)
- [Do (+1)](do/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [Phase 1: Deep Research and Planning (+3)](phase-1-deep-research-and-planning/SKILL.md)
- [Language Choice (+4)](language-choice/SKILL.md)
- [Pagination (+2)](pagination/SKILL.md)
- [Integration with Claude Code](integration-with-claude-code/SKILL.md)
- [.mcp.json for Team Sharing (+2)](mcpjson-for-team-sharing/SKILL.md)
- [Security Best Practices](security-best-practices/SKILL.md)
