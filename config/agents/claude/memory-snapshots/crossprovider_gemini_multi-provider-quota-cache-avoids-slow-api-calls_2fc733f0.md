---
name: crossprovider gemini multi-provider-quota-cache-avoids-slow-api-calls
description: Multi-provider quota cache avoids slow API calls
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [performance, multi-agent, caching]
---

WRK-108 tracks Claude/Codex/Gemini usage via ~/.cache/agent-quota.json (15-min TTL) parsed from local stats (Claude: ~/.claude/stats-cache.json, Codex: ~/.codex/history.jsonl, Gemini: estimated from session activity). Cache prevents startup slowdown when querying API endpoints; degrades gracefully on cache miss.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
