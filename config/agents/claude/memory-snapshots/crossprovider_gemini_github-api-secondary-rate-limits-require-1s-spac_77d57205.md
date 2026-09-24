---
name: crossprovider gemini github-api-secondary-rate-limits-require-1s-spac
description: GitHub API secondary rate limits require 1s spacing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [github-api, rate-limiting, reliability]
---

Respecting the hourly quota is insufficient; batch mutations need 1s sleep between calls plus exponential backoff on 429/5xx. Secondary limits are undocumented but real.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
