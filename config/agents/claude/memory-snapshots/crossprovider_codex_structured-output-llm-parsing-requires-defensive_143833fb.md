---
name: crossprovider codex structured-output-llm-parsing-requires-defensive
description: Structured-output LLM parsing requires defensive patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-integration, parsing, reliability]
---

When requesting JSON/YAML from external LLMs: (1) strip markdown fences before parsing, (2) handle parse failures gracefully (carry-forward prior state if applicable), (3) validate parsed content (e.g., domain whitelist for URLs), (4) use deterministic dedup (hash-based on stable fields, not position).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
