---
name: crossprovider gemini cli-tool-parameter-assumptions-require-live-retr
description: CLI tool parameter assumptions require live retrieval before pseudocode
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cli-tools, pseudocode-reliability, documentation-retrieval]
---

Plans that assume CLI behavior (e.g., `codex -p` for prompt file, `gemini -p`) without retrieving actual `--help` output or API docs often fail at TDD test write-time. Pseudocode must cite actual CLI invocation signatures; if documentation is unavailable, note it as a risk/blocker and define a fallback invocation strategy.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
