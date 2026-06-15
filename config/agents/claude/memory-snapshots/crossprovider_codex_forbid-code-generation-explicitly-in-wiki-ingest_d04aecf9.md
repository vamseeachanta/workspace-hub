---
name: crossprovider codex forbid-code-generation-explicitly-in-wiki-ingest
description: Forbid code generation explicitly in wiki-ingest prompts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [prompt-engineering, agent-guardrails]
---

Add guardrail: 'OUTPUT ONLY wiki content—never create scripts, .py, tests, or code of any kind.' Codex agent improvised .py and test files despite wiki-extract task; explicit forbid prevents scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
