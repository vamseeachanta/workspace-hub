---
name: crossprovider gemini tool-execution-context-determines-dependency-vis
description: Tool execution context determines dependency visibility
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [uv-python-runtime, dependency-isolation]
---

`uv tool run` (isolated environment) vs `uv run` (project context) have different dependency resolution. Tools run in isolation may fail silently to resolve third-party imports. Choose the right context for the tool's needs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
