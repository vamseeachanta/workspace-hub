---
name: crossprovider codex supply-chain-trust-gate-must-precede-executable-
description: Supply-chain trust gate must precede executable install
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [supply-chain, security, mcp-servers]
---

For MCP servers and vendored tools, complete source review (owner, permissions, transitive dependencies, commit pinning) before any `uvx` or `uv tool install` execution. Pinning a commit SHA is necessary but not sufficient—a compromised repo at that commit is still a supply-chain risk. Sequencing installs before trust review inverts the dependency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
