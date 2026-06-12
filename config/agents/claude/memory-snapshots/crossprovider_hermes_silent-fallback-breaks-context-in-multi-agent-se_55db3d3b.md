---
name: crossprovider hermes silent-fallback-breaks-context-in-multi-agent-se
description: Silent fallback breaks context in multi-agent setups
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-config, rate-limiting, context-stability]
---

Hermes switched default from copilot (Claude Sonnet) to codex (GPT-4.1) because copilot's silent mid-session fallback broke context. Different rate-limit cadences between providers cause hidden failures. Solution: dual OAuth creds with round-robin + explicit fallback chain.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
