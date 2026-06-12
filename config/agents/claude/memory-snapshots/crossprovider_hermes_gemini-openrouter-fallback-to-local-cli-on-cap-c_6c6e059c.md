---
name: crossprovider hermes gemini-openrouter-fallback-to-local-cli-on-cap-c
description: Gemini OpenRouter fallback to local CLI on cap/credit limits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-fallback, gemini, batch-execution]
---

When `hermes chat --provider openrouter --model gemini-2.5-pro` hits cap/credit limits in batch runs, switch to local `gemini -p` CLI. Observed multiple times across 2026-04-28 overnight batch; reliable workaround.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
