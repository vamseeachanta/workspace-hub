---
name: crossprovider gemini claude-p-batch-subprocess-over-api-for-classific
description: claude -p batch subprocess over API for classification tasks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [batch-classification, subprocess-pattern, sharding]
---

For batch classification (PDFs, documents), use `claude -p <prompt>` subprocess with `--shard N --total M` sharding instead of raw Anthropic SDK calls. Avoids credential exposure in code, enables trivial parallelization (each shard independent), and integrates with system timeout/monitoring. Requires `env.pop(CLAUDECODE)` to avoid session nesting.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
