---
name: crossprovider gemini multi-provider-agent-usage-tracking-divergence
description: Multi-provider agent usage tracking divergence
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ai-orchestration, usage-tracking, multi-provider]
---

Different AI providers store usage statistics in incompatible formats: Claude writes to ~/.claude/stats-cache.json (message counts), Codex to ~/.codex/history.jsonl (session entries), Gemini has no programmatic API. Solution: dedicated query script with 15-minute cache + statusline integration to avoid repeated API calls.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
