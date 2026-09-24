---
name: crossprovider codex supply-chain-security-review-must-precede-instal
description: Supply-chain security review must precede installation, not follow it
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [supply-chain-security, mcp-servers, sequencing, WRK-1055]
---

For remote components (MCP servers, packages, tools), the pre-install trust gate—reviewing source, permissions, transitive dependencies, rollback steps—must happen before any `uvx`/`uv tool install` execution. Documenting trust assessment after installation only, or pinning a commit SHA without upfront review, leaves a window for supply-chain compromise.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
