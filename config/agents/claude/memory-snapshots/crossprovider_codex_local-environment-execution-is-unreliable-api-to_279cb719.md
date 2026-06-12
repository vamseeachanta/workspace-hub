---
name: crossprovider codex local-environment-execution-is-unreliable-api-to
description: Local environment execution is unreliable; API/tool-based evidence is more robust
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [environment, execution-reliability, evidence-gathering]
---

Multiple worker sessions show local filesystem writes fail even on allowed paths, shell/CLI wrappers fail before command execution, and GitHub API mutations get cancelled. Plans should gather evidence via GitHub API, MCP tools, or read-only CLI where possible; local `uv run` for tests is riskier in adversarial-review contexts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
