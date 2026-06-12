---
name: crossprovider gemini secondary-abuse-limits-require-1s-minimum-sleep-
description: Secondary abuse limits require 1s minimum sleep and 429 detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [rate-limiting, api-safety, backoff-strategy]
---

GitHub and other APIs have undocumented secondary rate limits triggered by 2500+ rapid mutations in short windows. Hourly quota alone is insufficient. Implement 1s minimum sleep between API calls and exponential backoff on 429 (too many requests) responses. Batches of >500 items need 20+ minute execution windows.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
