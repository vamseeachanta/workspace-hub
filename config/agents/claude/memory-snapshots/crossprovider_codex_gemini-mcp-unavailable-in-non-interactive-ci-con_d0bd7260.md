---
name: crossprovider codex gemini-mcp-unavailable-in-non-interactive-ci-con
description: Gemini MCP unavailable in non-interactive CI contexts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [mcp, gemini, ci, authentication]
---

Gemini MCP connector requires interactive OAuth and fails with rc=41 in headless/non-interactive modes (CI, agent workflows). For multi-provider review in CI pipelines, fall back to Claude + Codex only and document Gemini as UNAVAILABLE rather than failing the build.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
